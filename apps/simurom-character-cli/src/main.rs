#![forbid(unsafe_code)]

use std::path::PathBuf;

use anyhow::{
  Context,
  Result
};
use clap::Parser;
use image::codecs::gif::GifEncoder;
use image::{
  Delay,
  Frame,
  ImageReader,
  RgbaImage
};
use simurom_schema::character::CharacterSpec;

#[derive(Parser, Debug)]
#[command(
  name = "simurom-character-cli"
)]
#[command(about = "Simurom Character Composite Preview and Blinking GIF Generator", long_about = None)]
struct Args {
  /// Path to character TOML file
  #[arg(short, long)]
  character: PathBuf,

  /// Output path for the default
  /// composite PNG preview
  #[arg(short = 'p', long)]
  output_png: Option<PathBuf>,

  /// Output path for the animated
  /// blinking GIF preview
  #[arg(short = 'g', long)]
  output_gif: Option<PathBuf>,

  /// Path to assets root directory
  #[arg(
    short,
    long,
    default_value = "assets"
  )]
  assets_dir: PathBuf
}

fn remove_white_background(
  img: &mut RgbaImage
) {
  let (width, height) =
    img.dimensions();
  if width == 0 || height == 0 {
    return;
  }

  let mut visited = vec![
    false;
    (width * height)
      as usize
  ];
  let mut queue =
    std::collections::VecDeque::new();

  // Start BFS from the four corners of
  // the image
  let corners = [
    (0, 0),
    (width - 1, 0),
    (0, height - 1),
    (width - 1, height - 1)
  ];

  for &(x, y) in &corners {
    let idx = (y * width + x) as usize;
    if !visited[idx] {
      let pixel = img.get_pixel(x, y);
      if pixel[0] > 240
        && pixel[1] > 240
        && pixel[2] > 240
        && pixel[3] > 0
      {
        visited[idx] = true;
        queue.push_back((x, y));
      }
    }
  }

  while let Some((cx, cy)) =
    queue.pop_front()
  {
    let pixel =
      img.get_pixel_mut(cx, cy);
    pixel[3] = 0;

    let neighbors = [
      (cx.wrapping_sub(1), cy),
      (cx + 1, cy),
      (cx, cy.wrapping_sub(1)),
      (cx, cy + 1)
    ];

    for &(nx, ny) in &neighbors {
      if nx < width && ny < height {
        let nidx =
          (ny * width + nx) as usize;
        if !visited[nidx] {
          let npixel =
            img.get_pixel(nx, ny);
          if npixel[0] > 240
            && npixel[1] > 240
            && npixel[2] > 240
            && npixel[3] > 0
          {
            visited[nidx] = true;
            queue.push_back((nx, ny));
          }
        }
      }
    }
  }
}

fn open_image(
  path: &std::path::Path
) -> Result<RgbaImage> {
  let img = ImageReader::open(path)
    .with_context(|| {
      format!(
        "Failed to open image at {:?}",
        path
      )
    })?
    .decode()
    .with_context(|| {
      format!(
        "Failed to decode image at \
         {:?}",
        path
      )
    })?;
  let mut rgba = img.to_rgba8();
  remove_white_background(&mut rgba);
  Ok(rgba)
}

struct LayerInfo {
  path:     PathBuf,
  offset_x: f32,
  offset_y: f32,
  scale:    Option<f32>,
  rotation: Option<f32>
}

fn bilinear_sample(
  img: &RgbaImage,
  x: f32,
  y: f32
) -> Option<image::Rgba<u8>> {
  let w = img.width() as f32;
  let h = img.height() as f32;
  if x < 0.0
    || x >= w - 1.0
    || y < 0.0
    || y >= h - 1.0
  {
    if x >= -0.5
      && x < w - 0.5
      && y >= -0.5
      && y < h - 0.5
    {
      let px =
        x.round().clamp(0.0, w - 1.0)
          as u32;
      let py =
        y.round().clamp(0.0, h - 1.0)
          as u32;
      return Some(
        *img.get_pixel(px, py)
      );
    }
    return None;
  }

  let x0 = x.floor() as u32;
  let x1 = x0 + 1;
  let y0 = y.floor() as u32;
  let y1 = y0 + 1;

  let dx = x - x.floor();
  let dy = y - y.floor();

  let p00 = img.get_pixel(x0, y0);
  let p10 = img.get_pixel(x1, y0);
  let p01 = img.get_pixel(x0, y1);
  let p11 = img.get_pixel(x1, y1);

  let mut channels = [0u8; 4];
  for c in 0..4 {
    let val0 = (p00[c] as f32)
      * (1.0 - dx)
      + (p10[c] as f32) * dx;
    let val1 = (p01[c] as f32)
      * (1.0 - dx)
      + (p11[c] as f32) * dx;
    let val =
      val0 * (1.0 - dy) + val1 * dy;
    channels[c] =
      val.round().clamp(0.0, 255.0)
        as u8;
  }

  Some(image::Rgba(channels))
}

fn composite_layers(
  base_size: (u32, u32),
  layers: &[LayerInfo]
) -> Result<RgbaImage> {
  let mut composite = RgbaImage::new(
    base_size.0,
    base_size.1
  );

  for layer in layers {
    if !layer.path.exists() {
      tracing::warn!(
        "Sprite file not found: {:?}",
        layer.path
      );
      continue;
    }

    let layer_img =
      open_image(&layer.path)?;
    let s = layer.scale.unwrap_or(1.0);
    let r =
      layer.rotation.unwrap_or(0.0);

    if s == 1.0 && r == 0.0 {
      let x_offset =
        layer.offset_x as i64;
      let y_offset =
        -(layer.offset_y as i64);
      image::imageops::overlay(
        &mut composite,
        &layer_img,
        x_offset,
        y_offset
      );
    } else {
      let target_cx =
        base_size.0 as f32 / 2.0;
      let target_cy =
        base_size.1 as f32 / 2.0;
      let src_cx =
        layer_img.width() as f32 / 2.0;
      let src_cy =
        layer_img.height() as f32 / 2.0;

      let angle_rad = -r.to_radians();
      let cos_a = angle_rad.cos();
      let sin_a = angle_rad.sin();

      for ty in 0..base_size.1 {
        for tx in 0..base_size.0 {
          let x3 = (tx as f32
            - target_cx)
            - layer.offset_x;
          let y3 = (target_cy
            - ty as f32)
            - layer.offset_y;

          let x2 =
            x3 * cos_a - y3 * sin_a;
          let y2 =
            x3 * sin_a + y3 * cos_a;

          let x1 = x2 / s;
          let y1 = y2 / s;

          let sx = x1 + src_cx;
          let sy = src_cy - y1;

          if let Some(sp) =
            bilinear_sample(
              &layer_img, sx, sy
            )
          {
            let sa =
              sp[3] as f32 / 255.0;
            if sa > 0.0 {
              let dp = composite
                .get_pixel_mut(tx, ty);
              let da =
                dp[3] as f32 / 255.0;

              let out_a =
                sa + da * (1.0 - sa);
              if out_a > 0.0 {
                for c in 0..3 {
                  let src_c =
                    sp[c] as f32;
                  let dest_c =
                    dp[c] as f32;
                  let blended = (src_c
                    * sa
                    + dest_c
                      * da
                      * (1.0 - sa))
                    / out_a;
                  dp[c] = blended
                    .round()
                    .clamp(0.0, 255.0)
                    as u8;
                }
                dp[3] = (out_a * 255.0)
                  .round()
                  .clamp(0.0, 255.0)
                  as u8;
              }
            }
          }
        }
      }
    }
  }

  Ok(composite)
}

fn resize_image(
  img: &RgbaImage,
  new_width: u32,
  new_height: u32
) -> RgbaImage {
  image::imageops::resize(
    img,
    new_width,
    new_height,
    image::imageops::FilterType::Lanczos3,
  )
}

fn main() -> Result<()> {
  // Initialize simple console logging
  tracing_subscriber::fmt()
    .with_writer(std::io::stderr)
    .with_target(false)
    .compact()
    .init();

  let args = Args::parse();

  if !args.character.exists() {
    anyhow::bail!(
      "Character TOML file not found: \
       {:?}",
      args.character
    );
  }

  // Load and deserialize the character
  // specification
  let content =
    std::fs::read_to_string(
      &args.character
    )
    .with_context(|| {
      format!(
        "Failed to read character \
         file {:?}",
        args.character
      )
    })?;
  let spec: CharacterSpec =
    toml::from_str(&content)
      .with_context(|| {
        format!(
          "Failed to parse character \
           TOML {:?}",
          args.character
        )
      })?;

  let char_cfg = &spec.character;
  let mut segments =
    char_cfg.segments.clone();
  let scale = char_cfg.scale;

  // Sort segments by layer_offset
  // (lowest first, so they are rendered
  // bottom-to-top)
  segments.sort_by(|a, b| {
    a.layer_offset
      .partial_cmp(&b.layer_offset)
      .unwrap_or(
        std::cmp::Ordering::Equal
      )
  });

  // Determine reference canvas size
  // from first valid segment image
  let mut base_size = (1254, 1254);
  for seg in &segments {
    let sprite_path =
      args.assets_dir.join(&seg.sprite);
    if sprite_path.exists() {
      if let Ok(reader) =
        ImageReader::open(&sprite_path)
      {
        if let Ok(dim) =
          reader.into_dimensions()
        {
          base_size = dim;
          break;
        }
      }
    }
  }

  tracing::info!(
    "Compositing character '{}' with \
     canvas size {:?}...",
    char_cfg.name,
    base_size
  );

  // 1. Generate Static PNG Preview
  //    (using default sprite
  //    configurations)
  if let Some(ref output_png) =
    args.output_png
  {
    let mut layers = Vec::new();
    for seg in &segments {
      let sprite_path = args
        .assets_dir
        .join(&seg.sprite);
      layers.push(LayerInfo {
        path:     sprite_path,
        offset_x: seg.offset.x,
        offset_y: seg.offset.y,
        scale:    seg.scale,
        rotation: seg.rotation
      });
    }

    let mut static_img =
      composite_layers(
        base_size, &layers
      )?;

    if scale != 1.0 {
      let new_width =
        (base_size.0 as f32 * scale)
          as u32;
      let new_height =
        (base_size.1 as f32 * scale)
          as u32;
      static_img = resize_image(
        &static_img,
        new_width,
        new_height
      );
    }

    if let Some(parent) =
      output_png.parent()
    {
      std::fs::create_dir_all(parent)?;
    }
    static_img
      .save(output_png)
      .with_context(|| {
        format!(
          "Failed to save static \
           preview to {:?}",
          output_png
        )
      })?;
    tracing::info!(
      "Successfully generated static \
       preview PNG at: {:?}",
      output_png
    );
  }

  // 2. Generate Looping GIF Preview for
  //    blinking animation behavior
  if let Some(ref output_gif) =
    args.output_gif
  {
    let mut blink_frames_paths =
      Vec::new();
    let mut eyes_segment_idx: Option<
      usize
    > = None;

    for (idx, seg) in
      segments.iter().enumerate()
    {
      if let Some(ref blink_cfg) =
        seg.blink
      {
        if let Some(ref frames) =
          blink_cfg.blink_frames
        {
          blink_frames_paths =
            frames.clone();
          eyes_segment_idx = Some(idx);
          break;
        }
      }
    }

    // Fallback check if simple
    // closed_sprite is present
    if blink_frames_paths.is_empty() {
      for (idx, seg) in
        segments.iter().enumerate()
      {
        if let Some(ref blink_cfg) =
          seg.blink
        {
          if let Some(
            ref closed_sprite
          ) = blink_cfg.closed_sprite
          {
            blink_frames_paths = vec![
              seg.sprite.clone(),
              closed_sprite.clone(),
            ];
            eyes_segment_idx =
              Some(idx);
            break;
          }
        }
      }
    }

    let Some(eyes_idx) =
      eyes_segment_idx
    else {
      tracing::warn!(
        "No blinking segment or \
         frames found in character \
         specification. Skipping GIF \
         generation."
      );
      return Ok(());
    };

    if blink_frames_paths.is_empty() {
      tracing::warn!(
        "No blinking frames found. \
         Skipping GIF generation."
      );
      return Ok(());
    }

    // Build full sequence of eye frames
    // for a single blink loop: open
    // -> partial1 -> partial2 ->
    // partial3 -> closed -> partial3 ->
    // partial2 -> partial1 -> open
    let active_sequence =
      blink_frames_paths.clone();
    let mut reverse_sequence: Vec<
      String
    > = Vec::new();
    if active_sequence.len() > 2 {
      for frame in active_sequence
        .iter()
        .skip(1)
        .take(active_sequence.len() - 2)
        .rev()
      {
        reverse_sequence
          .push(frame.clone());
      }
    }

    let mut full_blink_sequence =
      active_sequence;
    full_blink_sequence
      .extend(reverse_sequence);

    // We'll generate 45 frames total:
    // the blink transition sequence
    // followed by open/idle frames
    let total_gif_frames_count = 45;

    let frame_dur_seconds = segments
      [eyes_idx]
      .blink
      .as_ref()
      .and_then(|b| b.frame_duration)
      .unwrap_or(0.05);
    let frame_dur_ms =
      (frame_dur_seconds * 1000.0)
        as u64;

    let mut gif_frames = Vec::new();

    for i in 0..total_gif_frames_count {
      let current_eye_sprite = if i
        < full_blink_sequence.len()
      {
        &full_blink_sequence[i]
      } else {
        &blink_frames_paths[0]
      };

      let mut layers = Vec::new();
      for (idx, seg) in
        segments.iter().enumerate()
      {
        let sprite_path =
          if idx == eyes_idx {
            args
              .assets_dir
              .join(current_eye_sprite)
          } else {
            args
              .assets_dir
              .join(&seg.sprite)
          };
        layers.push(LayerInfo {
          path:     sprite_path,
          offset_x: seg.offset.x,
          offset_y: seg.offset.y,
          scale:    seg.scale,
          rotation: seg.rotation
        });
      }

      let mut frame_img =
        composite_layers(
          base_size, &layers
        )?;
      if scale != 1.0 {
        let new_width =
          (base_size.0 as f32 * scale)
            as u32;
        let new_height =
          (base_size.1 as f32 * scale)
            as u32;
        frame_img = resize_image(
          &frame_img, new_width,
          new_height
        );
      }

      let delay = Delay::from_saturating_duration(std::time::Duration::from_millis(frame_dur_ms));
      let frame = Frame::from_parts(
        frame_img, 0, 0, delay
      );
      gif_frames.push(frame);
    }

    if let Some(parent) =
      output_gif.parent()
    {
      std::fs::create_dir_all(parent)?;
    }

    let out_file =
      std::fs::File::create(output_gif)
        .with_context(|| {
          format!(
            "Failed to create output \
             GIF file at {:?}",
            output_gif
          )
        })?;
    let mut encoder =
      GifEncoder::new(out_file);
    encoder.set_repeat(image::codecs::gif::Repeat::Infinite)?;
    encoder
      .encode_frames(gif_frames)
      .with_context(|| {
      "Failed to encode frames into \
       animated GIF"
    })?;

    tracing::info!(
      "Successfully generated dynamic \
       blinking animated GIF at: {:?}",
      output_gif
    );
  }

  Ok(())
}
