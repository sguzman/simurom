use std::path::PathBuf;
use std::sync::OnceLock;

use anyhow::Context;
use clap::{
  Parser,
  Subcommand
};
use flatfekt_config::RootConfig;
use flatfekt_runtime::{
  LoadError,
  build_app,
  load_config,
  load_scene
};
use tracing::warn;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;

mod ui;

#[derive(Parser, Debug)]
#[command(name = "flatfekt")]
#[command(about = "TOML-driven 2D Bevy scene runner", long_about = None)]
struct Cli {
  /// Path to the control-pane config
  /// TOML.
  #[arg(
    long,
    default_value = ".config/flatfekt/\
                     flatfekt.toml"
  )]
  config: PathBuf,

  /// Use X11 instead of Wayland on
  /// Unix (Wayland remains the
  /// default).
  #[arg(long)]
  x11: bool,

  /// Override `logging.level`
  /// (trace|debug|info|warn|error).
  #[arg(long)]
  log_level: Option<String>,

  /// Override `logging.filter`
  /// (tracing filter string).
  #[arg(long)]
  log_filter: Option<String>,

  #[command(subcommand)]
  command: Command
}

#[derive(Subcommand, Debug)]
enum Command {
  /// Validate a scene TOML against the
  /// schema and current control pane.
  Validate { scene: PathBuf },
  /// Run a scene (overrides any
  /// configured `app.scene_path`).
  Run { scene: PathBuf },

  /// Run a scene's timeline headlessly
  /// (no window) and log dispatched
  /// events + patch application.
  TraceTimeline {
    scene:         PathBuf,
    /// Maximum number of fixed-dt
    /// steps to run.
    #[arg(long, default_value_t = 600)]
    max_steps:     u32,
    /// Optional maximum time (seconds)
    /// to run; overrides scene
    /// duration.
    #[arg(long)]
    max_time_secs: Option<f32>
  }
}

fn main() -> anyhow::Result<()> {
  let cli = Cli::parse();
  let cfg = load_config_or_fail_fast(
    &cli.config
  )?;
  init_tracing(
    &cfg,
    cli.log_level.as_deref(),
    cli.log_filter.as_deref()
  )?;

  match cli.command {
    | Command::Validate {
      scene
    } => {
      let _scene = load_scene(&scene)
        .map_err(|e| {
        match e {
          | LoadError::Scene {
            ..
          } => e,
          | LoadError::Config {
            ..
          } => e
        }
      })?;
      tracing::info!(path = %scene.display(), "scene valid");
      Ok(())
    }
    | Command::Run {
      scene
    } => {
      #[cfg(unix)]
      configure_unix_backend_env(
        &cfg, cli.x11
      )?;
      require_render_adapter(&cfg)?;
      let scene_file =
        load_scene(&scene)?;
      let scene_allows_inspector =
        scene_file
          .scene
          .playback
          .as_ref()
          .and_then(|p| {
            p.enable_introspection
          })
          .unwrap_or(false);

      let mut app = build_app(
        cfg.clone(),
        scene.clone(),
        scene_file
      )
      .context("build app")?;
      ui::maybe_add_ui_plugins(
        &cfg,
        scene_allows_inspector,
        &mut app
      )?;
      app.run();
      Ok(())
    }

    | Command::TraceTimeline {
      scene,
      max_steps,
      max_time_secs
    } => {
      let mut scene_file =
        load_scene(&scene)?;
      let opts =
        flatfekt_runtime::headless_timeline::HeadlessTimelineOptions {
          max_steps,
          max_time_secs
        };
      let res =
        flatfekt_runtime::headless_timeline::run_headless_timeline(
          &cfg,
          &mut scene_file,
          &opts
        )?;
      tracing::info!(
        ?res,
        "headless timeline run \
         complete"
      );
      Ok(())
    }
  }
}



fn load_config_or_fail_fast(
  path: &PathBuf
) -> anyhow::Result<RootConfig> {
  match load_config(path) {
    | Ok(cfg) => Ok(cfg),
    | Err(LoadError::Config {
      ..
    }) if !path.exists() => {
      warn!(path = %path.display(), "config file not found; using built-in defaults");
      let cfg = RootConfig {
        app:        None,
        logging:    None,
        platform:   None,
        render:     None,
        assets:     None,
        features:   None,
        runtime:    None,
        ui:         None,
        simulation: None
      };
      cfg.validate().context(
        "default config invalid"
      )?;
      Ok(cfg)
    }
    | Err(e) => Err(anyhow::anyhow!(e))
  }
}

fn init_tracing(
  cfg: &RootConfig,
  level_override: Option<&str>,
  filter_override: Option<&str>
) -> anyhow::Result<()> {
  let filter = filter_override
    .map(|s| s.to_owned())
    .or_else(|| {
      level_override
        .map(|s| s.to_owned())
    })
    .or_else(|| {
      cfg
        .logging
        .as_ref()
        .and_then(|l| {
          l.filter.as_deref()
        })
        .map(|s| s.to_owned())
    })
    .or_else(|| {
      cfg
        .logging
        .as_ref()
        .and_then(|l| {
          l.level.as_deref()
        })
        .map(|lvl| lvl.to_owned())
    })
    .or_else(|| {
      std::env::var("RUST_LOG").ok()
    })
    .unwrap_or_else(|| {
      "info".to_owned()
    });

  let env_filter =
    tracing_subscriber::EnvFilter::new(
      filter
    );
  let stderr_layer =
    tracing_subscriber::fmt::layer()
      .with_target(true)
      .with_level(true);
  let registry =
    tracing_subscriber::registry()
      .with(env_filter)
      .with(stderr_layer);

  if cfg.app_mode() == "dev" {
    let logs_dir = cache_logs_dir();
    std::fs::create_dir_all(&logs_dir)?;
    let file_name =
      run_log_file_name()?;
    let file_appender =
      tracing_appender::rolling::never(
        logs_dir, file_name
      );
    let (non_blocking, guard) =
      tracing_appender::non_blocking(
        file_appender
      );
    LOG_GUARD.set(guard).map_err(
      |_| {
        anyhow::anyhow!(
          "log guard already \
           initialized"
        )
      }
    )?;

    let file_layer =
      tracing_subscriber::fmt::layer()
        .with_ansi(false)
        .with_target(true)
        .with_level(true)
        .with_writer(non_blocking);

    registry.with(file_layer).init();
  } else {
    registry.init();
  }
  Ok(())
}

static LOG_GUARD: OnceLock<tracing_appender::non_blocking::WorkerGuard> = OnceLock::new();

fn cache_logs_dir() -> PathBuf {
  PathBuf::from(".cache")
    .join("flatfekt")
    .join("logs")
}

fn run_log_file_name()
-> anyhow::Result<String> {
  let now =
    std::time::SystemTime::now()
      .duration_since(
        std::time::UNIX_EPOCH
      )
      .context(
        "system time before unix epoch"
      )?;
  Ok(format!(
    "run-{}.log",
    now.as_secs()
  ))
}

fn require_render_adapter(
  cfg: &RootConfig
) -> anyhow::Result<()> {
  let rb = cfg.render_backend();
  let backends = match rb {
    | "vulkan" => wgpu::Backends::VULKAN,
    | "dx12" => wgpu::Backends::DX12,
    | "metal" => wgpu::Backends::METAL,
    | "auto" | _ => wgpu::Backends::all()
  };

  let instance =
    wgpu::Instance::new(wgpu::InstanceDescriptor {
      backends,
      ..wgpu::InstanceDescriptor::new_without_display_handle()
    });

  let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions {
    power_preference: wgpu::PowerPreference::HighPerformance,
    compatible_surface: None,
    force_fallback_adapter: false,
  })).context(format!("Failed to find a suitable {rb} adapter"))?;
  let info = adapter.get_info();
  tracing::info!(
    ?info,
    backend = rb,
    "Graphics adapter selected"
  );
  Ok(())
}

#[cfg(unix)]
fn configure_unix_backend_env(
  cfg: &RootConfig,
  x11: bool
) -> anyhow::Result<()> {
  let rb = cfg.render_backend();
  unsafe {
    std::env::set_var(
      "WGPU_BACKEND",
      rb
    );
  }

  let configured = cfg.unix_backend();
  let backend = if x11 {
    if configured != "x11" {
      tracing::warn!(
        configured,
        "overriding \
         platform.unix_backend to x11 \
         for this run"
      );
    }
    "x11"
  } else {
    configured
  };

  unsafe {
    std::env::set_var(
      "WINIT_UNIX_BACKEND",
      backend
    );
  }
  tracing::info!(
    backend,
    "unix backend selected"
  );

  preflight_display_env(backend)?;
  Ok(())
}

#[cfg(unix)]
fn preflight_display_env(
  ub: &str
) -> anyhow::Result<()> {
  match ub {
    | "x11" => {
      if std::env::var_os("DISPLAY")
        .is_none()
      {
        anyhow::bail!(
          "x11 selected but DISPLAY \
           is not set; run under an \
           X11 session (or Xwayland) \
           or set DISPLAY"
        );
      }
    }
    | "wayland" => {
      let has_wayland =
        std::env::var_os(
          "WAYLAND_DISPLAY"
        )
        .is_some()
          || std::env::var_os(
            "WAYLAND_SOCKET"
          )
          .is_some();
      if !has_wayland {
        anyhow::bail!(
          "wayland selected but \
           neither WAYLAND_DISPLAY \
           nor WAYLAND_SOCKET is set; \
           run under a Wayland session"
        );
      }
    }
    | _ => {}
  }
  Ok(())
}
