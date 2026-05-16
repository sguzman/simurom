use schemars::schema_for;
use simurom_schema::Scene;

fn main() {
  let schema = schema_for!(Scene);
  let json =
    serde_json::to_string_pretty(
      &schema
    )
    .unwrap();
  println!("{}", json);
}
