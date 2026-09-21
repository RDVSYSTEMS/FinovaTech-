-- ============================================================
-- FinovaTech v9 — Esquema de la base de datos
-- ============================================================
-- Modelo basado en el diagrama ER (FinovaTech.mwb):
--   Administrador 1─N Usuario 1─1 Estudiante 1─N Ingreso
--                                                 1─N Gasto
--                                                 1─N Presupuesto
--                                                 1─N Reporte
--   Usuario 1─N Agendamiento
--
-- Incluye (además de las 8 tablas):
--   * 4 TRIGGERS   -> mantienen al día estudiante.saldo_actual
--                     al insertar/eliminar ingresos y gastos.
--   * 4 STORED PROCEDURES -> sp_registrar_movimiento,
--                     sp_eliminar_movimiento, sp_resumen_mensual,
--                     sp_generar_reporte.
--   * 1 VISTA       -> vista_resumen_financiero (SQL complejo).
--
-- Ejecuta este archivo desde la consola de MySQL/XAMPP:
--     "" | mysql.exe -u root < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS finovatech
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE finovatech;

-- ------------------------------------------------------------
-- Tablas
-- ------------------------------------------------------------

-- Las entidades principales se crean antes de sus tablas dependientes para
-- que las claves foráneas puedan validarse desde el primer momento.

-- Tabla de roles y datos propios de administradores.
CREATE TABLE IF NOT EXISTS administrador (
    id  INT AUTO_INCREMENT PRIMARY KEY,
    rol VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- Cuenta de acceso: identidad, credenciales cifradas y rol del usuario.
CREATE TABLE IF NOT EXISTS usuario (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    email          VARCHAR(120) NOT NULL UNIQUE,
    username       VARCHAR(50)  NOT NULL UNIQUE,
    password       VARCHAR(255) NOT NULL,
    rol            ENUM('estudiante', 'empleado', 'administrador', 'padre') NOT NULL DEFAULT 'estudiante',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    administrador_id INT NULL,
    CONSTRAINT fk_usuario_administrador
        FOREIGN KEY (administrador_id) REFERENCES administrador(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- Perfil académico y saldo acumulado asociado a una única cuenta.
CREATE TABLE IF NOT EXISTS estudiante (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    grado       VARCHAR(30)  NOT NULL,
    institucion VARCHAR(100) NOT NULL,
    saldo_actual DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    usuario_id  INT NOT NULL,
    CONSTRAINT fk_estudiante_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_estudiante_usuario UNIQUE (usuario_id)
) ENGINE=InnoDB;

-- Dinero recibido por el estudiante, clasificado por categoría.
CREATE TABLE IF NOT EXISTS ingreso (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    monto        DECIMAL(12, 2) NOT NULL,
    fecha        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descripcion  VARCHAR(255) NOT NULL,
    categoria    VARCHAR(50)  NOT NULL,
    estudiante_id INT NOT NULL,
    CONSTRAINT fk_ingreso_estudiante
        FOREIGN KEY (estudiante_id) REFERENCES estudiante(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Dinero gastado por el estudiante, usado para calcular el saldo y presupuesto.
CREATE TABLE IF NOT EXISTS gasto (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    monto        DECIMAL(12, 2) NOT NULL,
    fecha        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descripcion  VARCHAR(255) NOT NULL,
    categoria    VARCHAR(50)  NOT NULL,
    estudiante_id INT NOT NULL,
    CONSTRAINT fk_gasto_estudiante
        FOREIGN KEY (estudiante_id) REFERENCES estudiante(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Límite de gasto definido para un estudiante durante un periodo.
CREATE TABLE IF NOT EXISTS presupuesto (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    monto_limite  DECIMAL(12, 2) NOT NULL,
    periodo       VARCHAR(50)  NOT NULL,
    fecha_inicio  DATE NOT NULL,
    fecha_fin     DATE NOT NULL,
    estudiante_id INT NOT NULL,
    CONSTRAINT fk_presupuesto_estudiante
        FOREIGN KEY (estudiante_id) REFERENCES estudiante(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Resumen financiero persistido cuando se genera un reporte.
CREATE TABLE IF NOT EXISTS reporte (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    tipo             VARCHAR(50)   NOT NULL,
    fecha_generacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_ingresos   DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    total_gastos     DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    estudiante_id    INT NOT NULL,
    CONSTRAINT fk_reporte_estudiante
        FOREIGN KEY (estudiante_id) REFERENCES estudiante(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Reserva de una sesión de educación financiera asociada al usuario.
CREATE TABLE IF NOT EXISTS agendamiento (
    -- Las citas pertenecen al usuario autenticado, no al saldo financiero.
    id          INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id  INT NOT NULL,
    fecha       DATE NOT NULL,
    hora        TIME NOT NULL,
    categoria   ENUM('reserva', 'consultoria', 'taller') NOT NULL,
    estado      ENUM('pendiente', 'confirmado', 'cancelado', 'completado') NOT NULL DEFAULT 'pendiente',
    comentarios VARCHAR(1000) NOT NULL DEFAULT '',
    creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_agendamiento_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Los ENUM limitan estados y categorías a valores conocidos por el formulario;
-- el backend también valida estos valores antes de insertar.

-- ============================================================
-- TRIGGERS
-- Se ejecutan automáticamente ante cambios en ingreso/gasto.
-- Cada uno recalcula estudiante.saldo_actual = ingresos - gastos
-- del estudiante afectado (es idempotente y no depende del orden).
-- ============================================================

-- Después de crear un ingreso, recalcula el saldo del estudiante.
DROP TRIGGER IF EXISTS trg_ingreso_after_insert;
DELIMITER //
CREATE TRIGGER trg_ingreso_after_insert AFTER INSERT ON ingreso
FOR EACH ROW
BEGIN
    UPDATE estudiante SET saldo_actual = (
        (SELECT COALESCE(SUM(monto), 0) FROM ingreso WHERE estudiante_id = NEW.estudiante_id)
      - (SELECT COALESCE(SUM(monto), 0) FROM gasto   WHERE estudiante_id = NEW.estudiante_id)
    ) WHERE id = NEW.estudiante_id;
END//
DELIMITER ;

-- Después de borrar un ingreso, recalcula el saldo del estudiante.
DROP TRIGGER IF EXISTS trg_ingreso_after_delete;
DELIMITER //
CREATE TRIGGER trg_ingreso_after_delete AFTER DELETE ON ingreso
FOR EACH ROW
BEGIN
    UPDATE estudiante SET saldo_actual = (
        (SELECT COALESCE(SUM(monto), 0) FROM ingreso WHERE estudiante_id = OLD.estudiante_id)
      - (SELECT COALESCE(SUM(monto), 0) FROM gasto   WHERE estudiante_id = OLD.estudiante_id)
    ) WHERE id = OLD.estudiante_id;
END//
DELIMITER ;

-- Después de crear un gasto, recalcula el saldo del estudiante.
DROP TRIGGER IF EXISTS trg_gasto_after_insert;
DELIMITER //
CREATE TRIGGER trg_gasto_after_insert AFTER INSERT ON gasto
FOR EACH ROW
BEGIN
    UPDATE estudiante SET saldo_actual = (
        (SELECT COALESCE(SUM(monto), 0) FROM ingreso WHERE estudiante_id = NEW.estudiante_id)
      - (SELECT COALESCE(SUM(monto), 0) FROM gasto   WHERE estudiante_id = NEW.estudiante_id)
    ) WHERE id = NEW.estudiante_id;
END//
DELIMITER ;

-- Después de borrar un gasto, recalcula el saldo del estudiante.
DROP TRIGGER IF EXISTS trg_gasto_after_delete;
DELIMITER //
CREATE TRIGGER trg_gasto_after_delete AFTER DELETE ON gasto
FOR EACH ROW
BEGIN
    UPDATE estudiante SET saldo_actual = (
        (SELECT COALESCE(SUM(monto), 0) FROM ingreso WHERE estudiante_id = OLD.estudiante_id)
      - (SELECT COALESCE(SUM(monto), 0) FROM gasto   WHERE estudiante_id = OLD.estudiante_id)
    ) WHERE id = OLD.estudiante_id;
END//
DELIMITER ;

-- ============================================================
-- STORED PROCEDURES
-- Envuelven las operaciones de negocio con validación incluida.
-- DELIMITER permite enviar cada bloque BEGIN...END como una unidad a MySQL.
-- ============================================================

-- Registra un movimiento (ingreso o gasto) validando tipo y monto.
DROP PROCEDURE IF EXISTS sp_registrar_movimiento;
DELIMITER //
CREATE PROCEDURE sp_registrar_movimiento(
    IN  p_estudiante_id INT,
    IN  p_tipo         VARCHAR(10),
    IN  p_descripcion  VARCHAR(255),
    IN  p_monto        DECIMAL(12, 2),
    IN  p_categoria    VARCHAR(50),
    IN  p_fecha        DATE,
    OUT p_id           INT,
    OUT p_mensaje      VARCHAR(255)
)
BEGIN
    SET p_id = NULL;

    IF p_monto IS NULL OR p_monto <= 0 THEN
        SET p_mensaje = 'El monto debe ser mayor a cero';
    ELSEIF p_tipo = 'Ingreso' THEN
        INSERT INTO ingreso (monto, descripcion, categoria, fecha, estudiante_id)
        VALUES (p_monto, p_descripcion, p_categoria, COALESCE(p_fecha, CURDATE()), p_estudiante_id);
        SET p_id = LAST_INSERT_ID();
        SET p_mensaje = 'Ingreso registrado correctamente';
    ELSEIF p_tipo = 'Gasto' THEN
        INSERT INTO gasto (monto, descripcion, categoria, fecha, estudiante_id)
        VALUES (p_monto, p_descripcion, p_categoria, COALESCE(p_fecha, CURDATE()), p_estudiante_id);
        SET p_id = LAST_INSERT_ID();
        SET p_mensaje = 'Gasto registrado correctamente';
    ELSE
        SET p_mensaje = 'Tipo de movimiento inválido';
    END IF;
END//
DELIMITER ;

-- Elimina un movimiento verificando que pertenezca al estudiante.
DROP PROCEDURE IF EXISTS sp_eliminar_movimiento;
DELIMITER //
CREATE PROCEDURE sp_eliminar_movimiento(
    IN  p_estudiante_id INT,
    IN  p_tipo          VARCHAR(10),
    IN  p_movimiento_id INT,
    OUT p_mensaje       VARCHAR(255)
)
BEGIN
    DECLARE v_afectadas INT DEFAULT 0;

    IF p_tipo = 'Ingreso' THEN
        DELETE FROM ingreso WHERE id = p_movimiento_id AND estudiante_id = p_estudiante_id;
        SET v_afectadas = ROW_COUNT();
    ELSEIF p_tipo = 'Gasto' THEN
        DELETE FROM gasto WHERE id = p_movimiento_id AND estudiante_id = p_estudiante_id;
        SET v_afectadas = ROW_COUNT();
    ELSE
        SET v_afectadas = -1;
    END IF;

    IF v_afectadas < 0 THEN
        SET p_mensaje = 'Tipo de movimiento inválido';
    ELSEIF v_afectadas = 0 THEN
        SET p_mensaje = 'El registro no existe o no te pertenece';
    ELSE
        SET p_mensaje = 'Registro eliminado correctamente';
    END IF;
END//
DELIMITER ;

-- Resumen de ingresos/gastos/balance de un estudiante en un mes.
DROP PROCEDURE IF EXISTS sp_resumen_mensual;
DELIMITER //
CREATE PROCEDURE sp_resumen_mensual(
    IN p_estudiante_id INT,
    IN p_anio          INT,
    IN p_mes           INT
)
BEGIN
    SELECT
        COALESCE(SUM(CASE WHEN t.tipo = 'Ingreso' THEN t.monto ELSE 0 END), 0) AS total_ingresos,
        COALESCE(SUM(CASE WHEN t.tipo = 'Gasto'   THEN t.monto ELSE 0 END), 0) AS total_gastos,
        COALESCE(SUM(CASE WHEN t.tipo = 'Ingreso' THEN t.monto ELSE -t.monto END), 0) AS balance
    FROM (
        SELECT 'Ingreso' AS tipo, monto FROM ingreso
        WHERE estudiante_id = p_estudiante_id
          AND YEAR(fecha) = p_anio AND MONTH(fecha) = p_mes
        UNION ALL
        SELECT 'Gasto' AS tipo, monto FROM gasto
        WHERE estudiante_id = p_estudiante_id
          AND YEAR(fecha) = p_anio AND MONTH(fecha) = p_mes
    ) t;
END//
DELIMITER ;

-- Genera un reporte guardado en la tabla "reporte".
DROP PROCEDURE IF EXISTS sp_generar_reporte;
DELIMITER //
CREATE PROCEDURE sp_generar_reporte(
    IN  p_estudiante_id INT,
    IN  p_tipo          VARCHAR(50),
    OUT p_reporte_id    INT
)
BEGIN
    INSERT INTO reporte (tipo, total_ingresos, total_gastos, estudiante_id)
    VALUES (
        p_tipo,
        (SELECT COALESCE(SUM(monto), 0) FROM ingreso WHERE estudiante_id = p_estudiante_id),
        (SELECT COALESCE(SUM(monto), 0) FROM gasto   WHERE estudiante_id = p_estudiante_id),
        p_estudiante_id
    );
    SET p_reporte_id = LAST_INSERT_ID();
END//
DELIMITER ;

-- ============================================================
-- VISTA
-- Resumen financiero de cada usuario: saldo, ingresos, gastos,
-- balance y categorías más gastadas (SUBQUERIES en el SELECT).
-- ============================================================

-- Consulta consolidada para mostrar el estado financiero de cada estudiante.
CREATE OR REPLACE VIEW vista_resumen_financiero AS
SELECT
    u.id            AS usuario_id,
    u.nombre,
    u.email,
    e.id            AS estudiante_id,
    e.grado,
    e.institucion,
    e.saldo_actual,
    COALESCE(i.total_ingresos, 0)       AS total_ingresos,
    COALESCE(g.total_gastos, 0)         AS total_gastos,
    COALESCE(i.total_ingresos, 0) - COALESCE(g.total_gastos, 0) AS balance,
    (SELECT c.categoria FROM gasto c
     WHERE c.estudiante_id = e.id
     GROUP BY c.categoria
     ORDER BY SUM(c.monto) DESC LIMIT 1) AS categoria_mas_gastada
FROM usuario u
JOIN estudiante e ON e.usuario_id = u.id
LEFT JOIN (
    SELECT estudiante_id, SUM(monto) AS total_ingresos
    FROM ingreso GROUP BY estudiante_id
) i ON i.estudiante_id = e.id
LEFT JOIN (
    SELECT estudiante_id, SUM(monto) AS total_gastos
    FROM gasto GROUP BY estudiante_id
) g ON g.estudiante_id = e.id;

-- El script es repetible: las tablas usan IF NOT EXISTS y los objetos
-- programables se reemplazan explícitamente antes de crearse.