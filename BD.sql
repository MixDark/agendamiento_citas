CREATE DATABASE IF NOT EXISTS consultorio_medico;
USE consultorio_medico;

CREATE TABLE doctores (
    id_doctor INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NOT NULL
);

CREATE TABLE pacientes (
    id_paciente INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    fecha_nacimiento DATE
);

CREATE TABLE citas (
    id_cita INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT,
    id_doctor INT,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    motivo VARCHAR(200),
    estado ENUM('programada', 'completada', 'cancelada') DEFAULT 'programada',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
    FOREIGN KEY (id_doctor) REFERENCES doctores(id_doctor),
    UNIQUE KEY unique_fecha_hora (fecha, hora)
);

INSERT INTO pacientes (id_paciente, nombre, apellido, telefono, email, fecha_nacimiento) VALUES
('9145325','Juan', 'Pérez', '1234567890', 'juan@email.com', '1980-01-15'),
('24986745', 'María', 'García', '0987654321', 'maria@email.com', '1990-05-20'),
('1245324974', 'Carlos', 'López', '5555555555', 'carlos@email.com', '1975-11-30');

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    es_admin BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requiere_cambio_password BOOLEAN DEFAULT FALSE
);

-- Insertar un usuario admin (password: admin123)
INSERT INTO usuarios (username, password_hash, nombre, es_admin, activo) VALUES (
    'admin', 
    'scrypt:32768:8:1$PM6tyKuu6Ic9J8dw$9223e18893a3a012ca3deda8db8b04677c3ec46615f0e6b9432096eb01c330a11e7c4a04cea52a63fd7e7d4c416ebaa7a15316784d8a3c8ab0923a643a923ede',
    'Administrador', TRUE, TRUE
);
