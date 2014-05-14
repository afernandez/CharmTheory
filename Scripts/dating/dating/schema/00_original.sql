SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';


CREATE SCHEMA IF NOT EXISTS `dating` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `dating` ;


-- -----------------------------------------------------
-- Table `user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `nick` varchar(45) DEFAULT NULL,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `email` varchar(64) NOT NULL,
  `gender` varchar(45) NOT NULL,
  `password` char(128) NOT NULL,
  `salt` char(32) NOT NULL,
  `confirmation` varchar(64) NOT NULL,
  `orientation` varchar(45) NOT NULL,
  `active` tinyint(4) NOT NULL DEFAULT '0',
  `birthday` datetime DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `country` varchar(45) DEFAULT NULL,
  `state` varchar(45) DEFAULT NULL,
  `city` varchar(45) DEFAULT NULL,
  `relationship` varchar(45) DEFAULT NULL,
  `ethnicity` varchar(45) DEFAULT NULL,
  `body` varchar(45) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `education` varchar(45) DEFAULT NULL,
  `college` varchar(128) DEFAULT NULL,
  `religion` varchar(45) DEFAULT NULL,
  `job` varchar(45) DEFAULT NULL,
  `income` int(11) DEFAULT NULL,
  `humor` varchar(45) DEFAULT NULL,
  `personality` varchar(45) DEFAULT NULL,
  `politics` varchar(45) DEFAULT NULL,
  `diet` varchar(45) DEFAULT NULL,
  `have_kids` varchar(45) DEFAULT NULL,
  `want_kids` varchar(45) DEFAULT NULL,
  `drink` varchar(45) DEFAULT NULL,
  `smoke` varchar(45) DEFAULT NULL,
  `pet` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `nick_UNIQUE` (`nick`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- -----------------------------------------------------
-- Table `user_essay`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `user_essay` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(256) NOT NULL,
  `info` varchar(2048) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id_idx` (`user_id`),
  CONSTRAINT `FK_essay_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- -----------------------------------------------------
-- Table `user_photo`
-- -----------------------------------------------------
CREATE TABLE `user_photo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `path` varchar(256) NOT NULL,
  `bytes` int(11) NOT NULL,
  `size` varchar(32) NOT NULL,
  `tag` varchar(256) DEFAULT NULL,
  `hash_md5` varchar(32) NOT NULL,
  `order` smallint(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`user_id`),
  KEY `FK_photo_user` (`user_id`),
  CONSTRAINT `FK_photo_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
