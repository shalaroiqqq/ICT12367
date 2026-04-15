# 🐾 VetCare Management System (Premium Edition)
**Status: Ready for Academic Submission**  
**Last Updated: April 2, 2026**

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**VetCare - Integrated Clinic Management & POS System** คือระบบบริหารจัดการคลินิกสัตว์เลี้ยงครบวงจรระดับองค์กร (Enterprise Grade) ที่ผสมผสานการออกแบบสไตล์ซอฟต์แวร์บริการ (SaaS) ขับเคลื่อนด้วยโครงสร้างเว็บแอปพลิเคชันจาก **Python Django** ที่มั่นคงแข็งแรง และรองรับการทำงานทั้งบน **SQLite (Portability)** และ **Microsoft SQL Server (High-Performance)**

---

## 👥 Meet The Developers (ทีมผู้พัฒนา)

| รหัสนิสิต / นักศึกษา | ชื่อ-นามสกุล | บทบาทหน้าที่ในโปรเจกต์ (Role) |
| :---: | :--- | :--- |
| **68082768** | **ธนกร พรานพนัส** | 🛠️ Backend & Database Architect |
| **68034713** | **ชนิตา คงศรี** | 🎨 Full-stack Developer & UI Design |
| **68046200** | **สินินาถ แช่มชู** | 🔍 Quality Assurance & System Analyst |

---

## 🚀 Key Features (ฟีเจอร์เด่นของระบบ)

### 📈 Advanced Dashboard
ระบบแดชบอร์ดสรุปยอดขายและสถิติต่างๆ ภายในคลินิกที่ถูกประมวลผลด้วยความรวดเร็วและใช้ **Chart.js** ในการแสดงภาพรวมสถิติแบบ Real-time (อาทิ สถิติรายได้, จำนวนคิวนัดหมายประจำวัน)

### 🏥 Clinic Operations Management
ระบบปฏิบัติการภายในคลินิกแบบครบสูตร:
* **🐾 Owner & Pet Directory:** ลงทะเบียนและจัดการฐานข้อมูลเจ้าของและสัตว์เลี้ยงอย่างเป็นระบบ
* **📅 Appointment Scheduling:** จัดการคิวและตารางนัดหมายล่วงหน้าที่เชื่อมโยงกับแพทย์แต่ละท่าน
* **📋 Medical Records:** ระบบบันทึกประวัติการรักษาที่ละเอียด เป็นระบบ พร้อมการจ่ายยาพ่วงในหน้าเดียว

### 🛍️ Professional POS & Inventory
ยกระดับการจัดการสินค้าคงคลังและการขายหน้าเคาน์เตอร์:
* **ระบบจัดการคลังยา:** คุมสต็อกยาทุกประเภทผ่านหน้าเว็บ
* **สต็อกอัตโนมัติ (Auto Stock Deduction):** ตัวเลขสต็อกยาลดลงทันทีเมื่อมีการกดบันทึกการรักษา
* **🖨️ Print-Friendly Report:** รองรับการเรียกดูบิลและ **"รายงานสรุปกำไรเบื้องต้น"** ที่จัดทำขึ้นมาให้สวยงามพอดีหน้ากระดาษผ่านการเขียนคำสั่ง **CSS Print Media** โดยเฉพาะ

### 🔒 Enterprise-Grade Security
* **Role-Based Access Control (RBAC):** แบ่งสิทธิ์ผู้ใช้งานระดับลึก (Admin / Staff / Vet)
* **URL Access Control:** ระบบล็อคสิทธิ์ ป้องกันการพิมพ์ URL แอบเข้าถึงหน้าการตั้งค่าโดยตรงหากไม่ได้รับอนุญาต

---

## 💾 Core Architecture & SQL Programmability (ขุมพลังฐานข้อมูลขั้นสูง)

จุดแข็งที่ทำให้โปรเจกต์ **VetCare** โดดเด่นกว่าระบบเว็บไซต์ทั่วไป คือการฝัง **Business Logic** หลายส่วนลงไปที่ระดับฐานข้อมูลโดยตรง เพื่อแก้ปัญหาด้านความเร็วและปกป้องข้อมูลในกรณีเว็บเซิร์ฟเวอร์ล่ม (Data Integrity) ประกอบไปด้วย:

* **📊 Complex Database Diagrams (ERD):** โครงสร้าง Relational Schema ที่ผ่านการออกแบบตามหลัก Normalization แบบสมบูรณ์
* **⚡ Stored Procedures:** ซ่อนความซับซ้อนไว้หลังบ้าน เช่น `sp_ApplyMemberDiscount` ในการคำนวณส่วนลดโดยตรงอย่างรวดเร็ว และการบันทึกประวัติรักษาร่วมกับการระบุตัวยาจบใน Transaction เดียว
* **🤖 Triggers & Audit Logs:**
  * **Auto-Deduction:** ตัดสต็อกยาทันทีเป๊ะๆ ทุกครั้งที่มีความเคลื่อนไหว
  * **Audit Trail (`myapp_audit_logs`):** ระบบกล้องวงจรปิดของข้อมูล เก็บทุกร่องรอยการแก้ไขข้อมูลสำคัญลงระบบ Log อย่างโปร่งใส
* **🔍 Functions & Views:** 
  * ใช้ **View** (เช่น `v_ClinicDashboard`) รวบรวมผลลัพธ์ที่สลับซับซ้อน ช่วยให้ฝั่ง Django ลดตรรกะการคิวรีซ้ำซ้อน
  * ใช้ **Scalar Functions** ช่วยคำนวณค่าสดๆ ในระดับ Row เช่น การแปลงวันเกิดสัตว์เลี้ยงเป็นอายุจริงแบบแม่นยำ

---

## 🛠️ Technology Stack

* **Back-end Framework:** Python, Django
* **Database Management System:** Microsoft SQL Server 2019 (MSSQL)
* **Front-end & UI:** HTML5, CSS3, JavaScript, Bootstrap 5
* **Reporting & Data Viz:** Chart.js, CSS Print Media
