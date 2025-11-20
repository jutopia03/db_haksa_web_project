-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: haksadb
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `login_id` varchar(30) NOT NULL,
  `password` varchar(100) NOT NULL,
  `role` varchar(20) NOT NULL,
  `student_id` int DEFAULT NULL,
  `professor_id` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE KEY `login_id_UNIQUE` (`login_id`),
  KEY `student_id_idx` (`student_id`),
  KEY `professor_id_idx` (`professor_id`),
  CONSTRAINT `fk_account_professor` FOREIGN KEY (`professor_id`) REFERENCES `professor` (`professor_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_account_student` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account`
--

LOCK TABLES `account` WRITE;
/*!40000 ALTER TABLE `account` DISABLE KEYS */;
INSERT INTO `account` VALUES (1,'admin','admin1234','admin',NULL,NULL,1),(2,'prof01','pw1234','professor',NULL,1,1),(3,'prof02','pw1234','professor',NULL,2,1),(4,'prof03','pw1234','professor',NULL,3,1),(5,'prof04','pw1234','professor',NULL,4,1),(6,'prof05','pw1234','professor',NULL,5,1),(7,'prof06','pw1234','professor',NULL,6,1),(8,'prof07','pw1234','professor',NULL,7,1),(9,'prof08','pw1234','professor',NULL,8,1),(10,'prof09','pw1234','professor',NULL,9,1),(11,'prof10','pw1234','professor',NULL,10,1),(12,'prof11','pw1234','professor',NULL,11,1),(13,'prof12','pw1234','professor',NULL,12,1),(14,'prof13','pw1234','professor',NULL,13,1),(15,'prof14','pw1234','professor',NULL,14,1),(16,'prof15','pw1234','professor',NULL,15,1),(17,'prof16','pw1234','professor',NULL,16,1),(18,'prof17','pw1234','professor',NULL,17,1),(19,'prof18','pw1234','professor',NULL,18,1),(20,'prof19','pw1234','professor',NULL,19,1),(21,'prof20','pw1234','professor',NULL,20,1),(22,'stu01','pw1234','student',1,NULL,1),(23,'stu02','pw1234','student',2,NULL,1),(24,'stu03','pw1234','student',3,NULL,1),(25,'stu04','pw1234','student',4,NULL,1),(26,'stu05','pw1234','student',5,NULL,1),(27,'stu06','pw1234','student',6,NULL,1),(28,'stu07','pw1234','student',7,NULL,1),(29,'stu08','pw1234','student',8,NULL,1),(30,'stu09','pw1234','student',9,NULL,1),(31,'stu10','pw1234','student',10,NULL,1),(32,'stu11','pw1234','student',11,NULL,1),(33,'stu12','pw1234','student',12,NULL,1),(34,'stu13','pw1234','student',13,NULL,1),(35,'stu14','pw1234','student',14,NULL,1),(36,'stu15','pw1234','student',15,NULL,1),(37,'stu16','pw1234','student',16,NULL,1),(38,'stu17','pw1234','student',17,NULL,1),(39,'stu18','pw1234','student',18,NULL,1),(40,'stu19','pw1234','student',19,NULL,1),(41,'stu20','pw1234','student',20,NULL,1);
/*!40000 ALTER TABLE `account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `course_name` varchar(50) NOT NULL,
  `credit` int DEFAULT NULL,
  `classroom` varchar(20) DEFAULT NULL,
  `hours` int DEFAULT NULL,
  `professor_id` int DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  KEY `professor_id_idx` (`professor_id`),
  CONSTRAINT `fk_course_professor` FOREIGN KEY (`professor_id`) REFERENCES `professor` (`professor_id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
INSERT INTO `course` VALUES (1,'프로그래밍기초',3,'E101-101',3,1),(2,'자료구조',3,'E101-102',3,2),(3,'회로이론',3,'E201-201',3,3),(4,'전자기학',3,'E201-202',3,4),(5,'기계제작실습',2,'E301-301',2,5),(6,'열역학',3,'E301-302',3,6),(7,'산업공학개론',3,'E401-401',3,7),(8,'품질경영',3,'E401-402',3,8),(9,'네트워크보안',3,'E501-501',3,9),(10,'암호학개론',3,'E501-502',3,10);
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `dept_id` int NOT NULL AUTO_INCREMENT,
  `dept_name` varchar(50) NOT NULL,
  `office` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'컴퓨터공학과','E101','042-000-1001'),(2,'전자공학과','E201','042-000-1002'),(3,'기계공학과','E301','042-000-1003'),(4,'산업경영공학과','E401','042-000-1004'),(5,'정보보안학과','E501','042-000-1005');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollment`
--

DROP TABLE IF EXISTS `enrollment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollment` (
  `enrollment_id` int NOT NULL,
  `student_id` int NOT NULL,
  `course_id` int NOT NULL,
  `year` int NOT NULL,
  `semester` int NOT NULL,
  `grade` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`enrollment_id`),
  KEY `student_id_idx` (`student_id`),
  KEY `course_id_idx` (`course_id`),
  CONSTRAINT `fk_enrollment_course` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_enrollment_student` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollment`
--

LOCK TABLES `enrollment` WRITE;
/*!40000 ALTER TABLE `enrollment` DISABLE KEYS */;
INSERT INTO `enrollment` VALUES (1,1,1,2024,1,'A'),(2,1,2,2024,1,'B+'),(3,2,1,2024,1,'A-'),(4,2,2,2024,1,'B'),(5,3,1,2024,1,'C+'),(6,3,2,2024,1,'B'),(7,4,1,2024,1,'A'),(8,4,2,2024,1,'A'),(9,5,3,2024,1,'B'),(10,5,4,2024,1,'A'),(11,6,3,2024,1,'B+'),(12,6,4,2024,1,'C'),(13,7,3,2024,1,'A-'),(14,7,4,2024,1,'B'),(15,8,3,2024,1,'B+'),(16,8,4,2024,1,'A'),(17,9,5,2024,1,'A'),(18,9,6,2024,1,'B'),(19,10,5,2024,1,'C+'),(20,10,6,2024,1,'B+'),(21,11,5,2024,1,'B'),(22,11,6,2024,1,'A-'),(23,12,5,2024,1,'A'),(24,12,6,2024,1,'A'),(25,13,7,2024,1,'B'),(26,13,8,2024,1,'B+'),(27,14,7,2024,1,'A'),(28,14,8,2024,1,'C'),(29,15,7,2024,1,'B+'),(30,15,8,2024,1,'A-'),(31,16,7,2024,1,'A'),(32,16,8,2024,1,'B'),(33,17,9,2024,1,'A-'),(34,17,10,2024,1,'B+'),(35,18,9,2024,1,'B'),(36,18,10,2024,1,'A'),(37,19,9,2024,1,'C+'),(38,19,10,2024,1,'B'),(39,20,9,2024,1,'A'),(40,20,10,2024,1,'A-');
/*!40000 ALTER TABLE `enrollment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professor`
--

DROP TABLE IF EXISTS `professor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `professor` (
  `professor_id` int NOT NULL,
  `professor_name` varchar(50) NOT NULL,
  `position` varchar(20) DEFAULT NULL,
  `hire_date` date DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `office` varchar(50) DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  PRIMARY KEY (`professor_id`),
  KEY `dept_id_idx` (`dept_id`),
  CONSTRAINT `fk_professor_department` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professor`
--

LOCK TABLES `professor` WRITE;
/*!40000 ALTER TABLE `professor` DISABLE KEYS */;
INSERT INTO `professor` VALUES (1,'김교수1','정교수','2010-03-01','010-1000-0001','E101-1',1),(2,'김교수2','부교수','2012-03-01','010-1000-0002','E101-2',1),(3,'박교수1','조교수','2015-03-01','010-1000-0003','E201-1',2),(4,'박교수2','정교수','2008-03-01','010-1000-0004','E201-2',2),(5,'최교수1','부교수','2013-09-01','010-1000-0005','E301-1',3),(6,'최교수2','조교수','2017-09-01','010-1000-0006','E301-2',3),(7,'이교수1','정교수','2009-03-01','010-1000-0007','E401-1',4),(8,'이교수2','부교수','2014-03-01','010-1000-0008','E401-2',4),(9,'정교수1','조교수','2018-03-01','010-1000-0009','E501-1',5),(10,'정교수2','정교수','2007-03-01','010-1000-0010','E501-2',5),(11,'한교수1','부교수','2011-03-01','010-1000-0011','E101-3',1),(12,'한교수2','조교수','2016-03-01','010-1000-0012','E101-4',1),(13,'오교수1','정교수','2006-03-01','010-1000-0013','E201-3',2),(14,'오교수2','부교수','2013-03-01','010-1000-0014','E201-4',2),(15,'윤교수1','조교수','2019-03-01','010-1000-0015','E301-3',3),(16,'윤교수2','정교수','2005-03-01','010-1000-0016','E301-4',3),(17,'홍교수1','부교수','2012-09-01','010-1000-0017','E401-3',4),(18,'홍교수2','조교수','2020-03-01','010-1000-0018','E401-4',4),(19,'배교수1','정교수','2004-03-01','010-1000-0019','E501-3',5),(20,'배교수2','부교수','2015-09-01','010-1000-0020','E501-4',5);
/*!40000 ALTER TABLE `professor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_id` int NOT NULL,
  `student_name` varchar(50) NOT NULL,
  `grade_level` int DEFAULT NULL,
  `gender` char(1) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  KEY `dept_id_idx` (`dept_id`),
  CONSTRAINT `fk_student_department` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (1,'학생1',1,'M','2005-01-10','010-2000-0001','대전시 동구 1번지',1),(2,'학생2',1,'F','2005-02-11','010-2000-0002','대전시 동구 2번지',1),(3,'학생3',2,'M','2004-03-12','010-2000-0003','대전시 동구 3번지',1),(4,'학생4',2,'F','2004-04-13','010-2000-0004','대전시 동구 4번지',1),(5,'학생5',1,'M','2005-05-14','010-2000-0005','대전시 서구 5번지',2),(6,'학생6',2,'F','2004-06-15','010-2000-0006','대전시 서구 6번지',2),(7,'학생7',3,'M','2003-07-16','010-2000-0007','대전시 서구 7번지',2),(8,'학생8',3,'F','2003-08-17','010-2000-0008','대전시 서구 8번지',2),(9,'학생9',1,'M','2005-09-18','010-2000-0009','대전시 유성구 9번지',3),(10,'학생10',2,'F','2004-10-19','010-2000-0010','대전시 유성구 10번지',3),(11,'학생11',3,'M','2003-11-20','010-2000-0011','대전시 유성구 11번지',3),(12,'학생12',4,'F','2002-12-21','010-2000-0012','대전시 유성구 12번지',3),(13,'학생13',1,'M','2005-01-22','010-2000-0013','대전시 중구 13번지',4),(14,'학생14',2,'F','2004-02-23','010-2000-0014','대전시 중구 14번지',4),(15,'학생15',3,'M','2003-03-24','010-2000-0015','대전시 중구 15번지',4),(16,'학생16',4,'F','2002-04-25','010-2000-0016','대전시 중구 16번지',4),(17,'학생17',1,'M','2005-05-26','010-2000-0017','대전시 대덕구 17번지',5),(18,'학생18',2,'F','2004-06-27','010-2000-0018','대전시 대덕구 18번지',5),(19,'학생19',3,'M','2003-07-28','010-2000-0019','대전시 대덕구 19번지',5),(20,'학생20',4,'F','2002-08-29','010-2000-0020','대전시 대덕구 20번지',5);
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-20 22:11:53
