-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 31, 2025 at 03:27 AM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `apsi`
--

-- --------------------------------------------------------

--
-- Table structure for table `material`
--

CREATE TABLE `material` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `level` varchar(255) NOT NULL,
  `part_code` varchar(255) NOT NULL,
  `deskripsi` varchar(255) NOT NULL,
  `lot_size` varchar(255) NOT NULL,
  `UOM` varchar(255) NOT NULL,
  `stok` bigint(255) NOT NULL,
  `status` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `material`
--

INSERT INTO `material` (`id`, `level`, `part_code`, `deskripsi`, `lot_size`, `UOM`, `stok`, `status`, `created_at`, `updated_at`) VALUES
(1, '0', 'A01', 'Espresso Machine', '1', 'Pcs', `1`, 'Make', '2024-05-21 22:51:48', '2024-05-21 22:51:48'),
(2, '1', 'B01', 'Portafilter', '1', 'Pcs', `1`, 'Make', '2024-05-21 22:51:48', '2024-05-21 22:51:48'),
(3, '2', 'C04', 'Bolt L M12 x 1.25 x 25', '2', 'Pcs', `1`, 'Buy', '2024-05-21 22:51:48', '2024-05-21 22:51:48'),
(4, '2', 'C05', 'Nut M10', '2', 'Pcs', `1`, 'Buy', '2024-05-21 22:51:48', '2024-05-21 22:51:48'),
(5, '3', 'D03', 'Bolt L M5 x 1.25 x 16', '2', 'Pcs', `1`, 'Buy', '2024-05-21 22:51:48', '2024-05-21 22:51:48');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `material`
--
ALTER TABLE `material`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `material`
--
ALTER TABLE `material`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
