-- =====================================================
-- Production Tables Schema for CV MAN System
-- Database: fri108_cvman
-- =====================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- =====================================================
-- Table structure for table `mps` (Master Production Schedule)
-- =====================================================

CREATE TABLE `mps` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `product` varchar(255) NOT NULL,
  `product_quantity` int(11) NOT NULL,
  `schedule` date NOT NULL,
  `status` enum('Planned','In Progress','Completed','Cancelled') NOT NULL DEFAULT 'Planned',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Table structure for table `material`
-- =====================================================

CREATE TABLE `material` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `material_code` varchar(100) NOT NULL,
  `material` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `lot_size` int(11) NOT NULL,
  `uom` varchar(50) NOT NULL,
  `status` enum('available','in deliveries','rejected') NOT NULL DEFAULT 'available',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Table structure for table `procurement`
-- =====================================================

CREATE TABLE `procurement` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `request_goods` varchar(255) NOT NULL,
  `date_request` date NOT NULL,
  `date_needed` date NOT NULL,
  `quantity` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Indexes for table `mps`
-- =====================================================

ALTER TABLE `mps`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_mps_schedule` (`schedule`),
  ADD KEY `idx_mps_status` (`status`),
  ADD KEY `idx_mps_product` (`product`);

-- =====================================================
-- Indexes for table `material`
-- =====================================================

ALTER TABLE `material`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_material_code` (`material_code`),
  ADD KEY `idx_material_status` (`status`),
  ADD KEY `idx_material_name` (`material`),
  ADD KEY `idx_material_uom` (`uom`);

-- =====================================================
-- Indexes for table `procurement`
-- =====================================================

ALTER TABLE `procurement`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_procurement_date_needed` (`date_needed`),
  ADD KEY `idx_procurement_date_request` (`date_request`),
  ADD KEY `idx_procurement_goods` (`request_goods`);

-- =====================================================
-- AUTO_INCREMENT for tables
-- =====================================================

ALTER TABLE `mps`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE `material`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE `procurement`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

-- =====================================================
-- Additional Constraints and Comments
-- =====================================================

-- Add check constraints for positive values
ALTER TABLE `mps` 
  ADD CONSTRAINT `chk_mps_quantity` CHECK (`product_quantity` > 0);

ALTER TABLE `material` 
  ADD CONSTRAINT `chk_material_lot_size` CHECK (`lot_size` > 0);

ALTER TABLE `procurement` 
  ADD CONSTRAINT `chk_procurement_quantity` CHECK (`quantity` > 0),
  ADD CONSTRAINT `chk_procurement_dates` CHECK (`date_needed` >= `date_request`);

-- Add table comments
ALTER TABLE `mps` COMMENT = 'Master Production Schedule - tracks production planning and scheduling';
ALTER TABLE `material` COMMENT = 'Material Availability - manages material inventory and status';
ALTER TABLE `procurement` COMMENT = 'Procurement Requests - handles material procurement requests';

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;