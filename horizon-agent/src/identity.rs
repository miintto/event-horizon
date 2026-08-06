use std::path::Path;

use anyhow::{Context, Result};
use uuid::Uuid;

pub fn load_or_create_agent_uuid(path: &Path) -> Result<Uuid> {
    if path.exists() {
        let raw = std::fs::read_to_string(path)
            .with_context(|| format!("failed to read agent id file: {}", path.display()))?;
        let uuid = Uuid::parse_str(raw.trim())
            .with_context(|| format!("invalid agent id in file: {}", path.display()))?;
        return Ok(uuid);
    }

    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent).with_context(|| {
            format!("failed to create agent id directory: {}", parent.display())
        })?;
    }

    let agent_uuid = Uuid::new_v4();
    std::fs::write(path, agent_uuid.to_string())
        .with_context(|| format!("failed to write agent id file: {}", path.display()))?;
    Ok(agent_uuid)
}
