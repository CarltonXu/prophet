-- Add platform_tag_relations table for platform-tag relationships
CREATE TABLE IF NOT EXISTS platform_tag_relations (
    platform_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (platform_id, tag_id),
    FOREIGN KEY (platform_id) REFERENCES virtualization_platforms(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES host_tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_platform_tag_relations_platform_id ON platform_tag_relations(platform_id);
CREATE INDEX IF NOT EXISTS idx_platform_tag_relations_tag_id ON platform_tag_relations(tag_id);

