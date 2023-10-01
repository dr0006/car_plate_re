/*
  2023-09-30 16:34
  用户: FxDr
  服务器: FXX-LEGION
  数据库: car_plate_re
  应用程序: car_plate_re 
*/

-- users用户表建表语句
CREATE TABLE users
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(255),
    email      VARCHAR(255) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 注册时间，默认为当前时间
);

-- 修改自增初始值为10001
ALTER TABLE users
    AUTO_INCREMENT = 10001;

-- --------------------------------------------------------------


-- car_plate车牌表，用来存储用户识别过的车牌等信息
CREATE TABLE car_plate
(
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    user_email         VARCHAR(255),                       -- 用户邮箱列
    image_url          VARCHAR(255) NOT NULL,              -- 用于存储图片
    recognition_result VARCHAR(50),
    confidence         FLOAT,                              -- 置信度列
    timestamp          TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 时间戳，记录识别操作的时间
);

