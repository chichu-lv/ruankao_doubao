# 更新与迁移

公开源码 ZIP 安装不需要 Git。重复运行 `scripts/install_public_windows.ps1` 会恢复原快照，不会自动更新或覆盖已有学习数据。

明确需要升级时，由豆包从同一公开仓库 main 下载到新的独立版本目录、运行本地检查，再按以下迁移约束备份和迁移当前项目绑定与私有资料索引。迁移前展示原/新目录；未经用户确认不批量覆盖旧目录。新版本可读到相同状态库、资料引用和检查点后才切换；保留旧目录用于回退。不要让新用户配置 SSH、Git 用户名或执行 git pull。

已有 Git 克隆可以继续使用其版本管理，但不作为新用户部署前提。

## Schema migration

Migrations live in `schemas/migrations/` and are ordered, versioned and backup-gated. `0001-initial.json` creates only the named private ArchitectPass tables and unique logical keys. It may not delete or rename pre-existing user data. A rollback first exports all created tables, then requires explicit confirmation before removing only objects created by that migration.
