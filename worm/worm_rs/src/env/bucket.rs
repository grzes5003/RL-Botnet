
type ObsType = i32;

trait Bucket {
    fn discretize_state(&self) -> ObsType;
}
