-- ============================================================
-- 智能校园失物招领系统 - 数据库建表脚本
-- ============================================================
-- 版本: v1.0
-- 更新: 2025-03-22
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- --------------------------------------------
-- 1. 用户表
-- --------------------------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username`      VARCHAR(64)     NOT NULL COMMENT '用户名/昵称',
    `password_hash` VARCHAR(255)    NOT NULL COMMENT '密码哈希',
    `phone`         VARCHAR(20)     DEFAULT NULL COMMENT '手机号',
    `student_id`    VARCHAR(32)     DEFAULT NULL COMMENT '学号（可选，来源：PRD 学号登录）',
    `avatar`        VARCHAR(512)    DEFAULT NULL COMMENT '头像URL',
    `role`          TINYINT         NOT NULL DEFAULT 1 COMMENT '角色：1普通用户 2管理员',
    `status`        TINYINT         NOT NULL DEFAULT 1 COMMENT '状态：1正常 0禁用',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_phone` (`phone`),
    UNIQUE KEY `uk_student_id` (`student_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- --------------------------------------------
-- 2. 地点表（校园地点，支持 LBS 打卡）
-- --------------------------------------------
DROP TABLE IF EXISTS `location`;
CREATE TABLE `location` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '地点ID',
    `name`        VARCHAR(128)    NOT NULL COMMENT '地点名称',
    `campus`      VARCHAR(64)     DEFAULT NULL COMMENT '校区',
    `building`    VARCHAR(64)     DEFAULT NULL COMMENT '楼栋',
    `floor`       VARCHAR(32)     DEFAULT NULL COMMENT '楼层',
    `longitude`   DECIMAL(10, 7)  DEFAULT NULL COMMENT '经度',
    `latitude`    DECIMAL(10, 7)  DEFAULT NULL COMMENT '纬度',
    `created_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_campus` (`campus`),
    KEY `idx_coord` (`longitude`, `latitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='地点表';

-- --------------------------------------------
-- 3. 物品类型表（YOLO 识别类别，来源：PPT）
-- --------------------------------------------
DROP TABLE IF EXISTS `item_type`;
CREATE TABLE `item_type` (
    `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '类型ID',
    `name`       VARCHAR(64)     NOT NULL COMMENT '类型名称（如：钥匙、钱包、杯子）',
    `code`       VARCHAR(32)     NOT NULL COMMENT '类型编码',
    `parent_id`  BIGINT UNSIGNED DEFAULT 0 COMMENT '父级ID，0为顶级',
    `sort`       INT             DEFAULT 0 COMMENT '排序',
    `created_at` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_code` (`code`),
    KEY `idx_parent` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物品类型表（YOLO类别）';

-- 初始化常见校园物品类型（补充：PPT 提及钥匙、钱包、杯子等）
INSERT INTO `item_type` (`name`, `code`, `parent_id`, `sort`) VALUES
('钥匙', 'key', 0, 1),
('钱包', 'wallet', 0, 2),
('杯子', 'cup', 0, 3),
('手机', 'phone', 0, 4),
('校园卡', 'campus_card', 0, 5),
('雨伞', 'umbrella', 0, 6),
('书包', 'bag', 0, 7),
('耳机', 'earphone', 0, 8),
('证件', 'id_card', 0, 9),
('其他', 'other', 0, 99);

-- --------------------------------------------
-- 4. 物品表（失物/招领主表）
-- --------------------------------------------
DROP TABLE IF EXISTS `item`;
CREATE TABLE `item` (
    `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '物品ID',
    `user_id`         BIGINT UNSIGNED NOT NULL COMMENT '发布者ID',
    `item_type`       TINYINT         NOT NULL COMMENT '发布类型：1寻物 2招领',
    `item_type_id`    BIGINT UNSIGNED DEFAULT NULL COMMENT '物品类型ID（YOLO识别结果）',
    `title`           VARCHAR(128)    NOT NULL COMMENT '标题',
    `description`     TEXT            DEFAULT NULL COMMENT '物品描述',
    `status`          TINYINT         NOT NULL DEFAULT 1 COMMENT '状态：1待认领/寻找中 2沟通中 3已归还',
    `location_id`     BIGINT UNSIGNED DEFAULT NULL COMMENT '地点ID',
    `location_detail` VARCHAR(256)    DEFAULT NULL COMMENT '地点补充说明',
    `lost_found_time` DATETIME        DEFAULT NULL COMMENT '丢失/拾取时间',
    `contact_info`    VARCHAR(256)    DEFAULT NULL COMMENT '联系方式（可脱敏展示）',
    `view_count`      INT             NOT NULL DEFAULT 0 COMMENT '浏览次数',
    `created_at`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_item_type` (`item_type`),
    KEY `idx_item_type_id` (`item_type_id`),
    KEY `idx_status` (`status`),
    KEY `idx_location` (`location_id`),
    KEY `idx_time` (`lost_found_time`),
    KEY `idx_created` (`created_at`),
    CONSTRAINT `fk_item_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_item_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_item_type` FOREIGN KEY (`item_type_id`) REFERENCES `item_type` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物品表（失物/招领）';

-- --------------------------------------------
-- 5. 物品图片表（含 OCR、YOLO 识别结果）
-- --------------------------------------------
DROP TABLE IF EXISTS `item_image`;
CREATE TABLE `item_image` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '图片ID',
    `item_id`       BIGINT UNSIGNED NOT NULL COMMENT '物品ID',
    `image_url`     VARCHAR(512)    NOT NULL COMMENT '图片URL',
    `sort_order`    INT             NOT NULL DEFAULT 0 COMMENT '排序',
    `ocr_text`      TEXT            DEFAULT NULL COMMENT 'OCR提取的文本（来源：PPT OCR模块）',
    `yolo_type_id`  BIGINT UNSIGNED DEFAULT NULL COMMENT 'YOLO识别的物品类型ID',
    `yolo_bbox`     JSON            DEFAULT NULL COMMENT 'YOLO框选坐标 [x1,y1,x2,y2]',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_item` (`item_id`),
    KEY `idx_yolo_type` (`yolo_type_id`),
    FULLTEXT KEY `ft_ocr_text` (`ocr_text`),
    CONSTRAINT `fk_image_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_image_yolo_type` FOREIGN KEY (`yolo_type_id`) REFERENCES `item_type` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物品图片表';

-- --------------------------------------------
-- 6. 物品特征向量表（CLIP 多模态特征，来源：PPT）
-- --------------------------------------------
-- 补充说明：CLIP 向量通常 512 维，此处以 JSON 存储。生产环境建议迁移至 Milvus/pgvector 等向量库以提升检索性能。
DROP TABLE IF EXISTS `item_feature`;
CREATE TABLE `item_feature` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `item_id`       BIGINT UNSIGNED NOT NULL COMMENT '物品ID',
    `image_id`      BIGINT UNSIGNED DEFAULT NULL COMMENT '图片ID（主图通常为第一张）',
    `feature_type`  TINYINT         NOT NULL DEFAULT 1 COMMENT '类型：1图片向量 2文本向量',
    `feature_vector` JSON           NOT NULL COMMENT '特征向量，如 [0.1,-0.2,...]',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_item_image` (`item_id`, `image_id`, `feature_type`),
    KEY `idx_item` (`item_id`),
    CONSTRAINT `fk_feature_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_feature_image` FOREIGN KEY (`image_id`) REFERENCES `item_image` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物品特征向量表（CLIP）';

-- --------------------------------------------
-- 7. 消息表（站内消息，来源：PRD 联系方式方案）
-- --------------------------------------------
DROP TABLE IF EXISTS `message`;
CREATE TABLE `message` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    `from_user_id` BIGINT UNSIGNED NOT NULL COMMENT '发送者ID',
    `to_user_id`   BIGINT UNSIGNED NOT NULL COMMENT '接收者ID',
    `item_id`      BIGINT UNSIGNED NOT NULL COMMENT '关联物品ID',
    `content`      TEXT            NOT NULL COMMENT '消息内容',
    `is_read`      TINYINT         NOT NULL DEFAULT 0 COMMENT '是否已读：0未读 1已读',
    `created_at`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_to_user` (`to_user_id`),
    KEY `idx_item` (`item_id`),
    KEY `idx_created` (`created_at`),
    CONSTRAINT `fk_msg_from` FOREIGN KEY (`from_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_msg_to` FOREIGN KEY (`to_user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_msg_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='站内消息表';

-- --------------------------------------------
-- 8. 用户行为日志表（协同过滤、推荐，来源：PPT 数据存储层）
-- --------------------------------------------
DROP TABLE IF EXISTS `behavior_log`;
CREATE TABLE `behavior_log` (
    `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id`       BIGINT UNSIGNED DEFAULT NULL COMMENT '用户ID（未登录可为空）',
    `item_id`       BIGINT UNSIGNED NOT NULL COMMENT '物品ID',
    `behavior_type` VARCHAR(32)     NOT NULL COMMENT '行为类型：view/click_contact/favorite/search',
    `extra`         JSON            DEFAULT NULL COMMENT '扩展信息，如搜索关键词',
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_item` (`item_id`),
    KEY `idx_behavior` (`behavior_type`),
    KEY `idx_created` (`created_at`),
    CONSTRAINT `fk_behavior_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_behavior_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户行为日志表';

-- --------------------------------------------
-- 9. 用户收藏表
-- --------------------------------------------
DROP TABLE IF EXISTS `user_favorite`;
CREATE TABLE `user_favorite` (
    `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `user_id`    BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `item_id`    BIGINT UNSIGNED NOT NULL COMMENT '物品ID',
    `created_at` DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_item` (`user_id`, `item_id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_item` (`item_id`),
    CONSTRAINT `fk_fav_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fav_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏表';

-- --------------------------------------------
-- 10. 识别日志表（YOLO/OCR 调用记录，来源：PPT 数据存储层）
-- --------------------------------------------
DROP TABLE IF EXISTS `recognition_log`;
CREATE TABLE `recognition_log` (
    `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `item_id`      BIGINT UNSIGNED DEFAULT NULL COMMENT '物品ID',
    `image_id`     BIGINT UNSIGNED DEFAULT NULL COMMENT '图片ID',
    `model_type`   VARCHAR(32)     NOT NULL COMMENT '模型类型：yolo/ocr/clip',
    `input_info`   JSON            DEFAULT NULL COMMENT '输入信息',
    `output_info`  JSON            DEFAULT NULL COMMENT '输出结果',
    `cost_ms`      INT             DEFAULT NULL COMMENT '耗时(毫秒)',
    `created_at`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_item` (`item_id`),
    KEY `idx_model` (`model_type`),
    KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='识别日志表（YOLO/OCR/CLIP）';

-- --------------------------------------------
-- 11. 系统配置表（五维权重等可配置项，来源：PRD 补充说明）
-- --------------------------------------------
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
    `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `config_key`  VARCHAR(64)     NOT NULL COMMENT '配置键',
    `config_value` VARCHAR(512)   NOT NULL COMMENT '配置值',
    `description` VARCHAR(256)    DEFAULT NULL COMMENT '说明',
    `created_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 初始化五维权重配置（来源：PPT）
INSERT INTO `system_config` (`config_key`, `config_value`, `description`) VALUES
('weight_image', '0.4', '图像相似度权重'),
('weight_text', '0.3', '文本相似度权重'),
('weight_location', '0.2', '地点距离权重'),
('weight_time', '0.1', '时间差权重'),
('recommend_top_n', '10', '相关推荐返回数量');

SET FOREIGN_KEY_CHECKS = 1;
