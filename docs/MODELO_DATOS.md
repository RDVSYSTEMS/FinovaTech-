# MODELO DE DATOS — FinovaTech v9

Base de datos `finovatech` en MySQL/MariaDB (XAMPP). Mobilidad: utf8mb4.

## 1. Diagrama de relaciones (ER)

```
administrador 1─N usuario 1─1 estudiante 1─N ingreso
                                        ├──N gasto
                                        ├──N presupuesto
                                        └──N reporte
```

## 2. Tablas

### administrador
| Columna | Tipo | Notas |
|---|---|---|
| id | INT PK AI | |
| rol | VARCHAR(50) NOT NULL | |

### usuario
| Columna | Tipo | Notas |
|---|---|---|
| id | INT PK AI | |
| nombre | VARCHAR(100) NOT NULL | |
| email | VARCHAR(120) NOT NULL UNIQUE | |
| username | VARCHAR(50) NOT NULL UNIQUE | |
| password | VARCHAR(255) NOT NULL | hash (werkzeug) |
| rol | ENUM(estudiante, empleado, administrador, padre) | default estudiante |
| fecha_registro | TIMESTAMP | default CURRENT_TIMESTAMP |
| administrador_id | INT NULL FK → administrador.id | ON DELETE SET NULL |

### estudiante
| Columna | Tipo | Notas |
|---|---|---|
| id | INT PK AI | |
| grado | VARCHAR(30) NOT NULL | |
| institucion | VARCHAR(100) NOT NULL | |
| saldo_actual | DECIMAL(12,2) default 0 | mantenido por TRIGGERS |
| usuario_id | INT NOT NULL UNIQUE FK → usuario.id | ON DELETE CASCADE, 1 a 1 |

### ingreso
| Columna | Tipo | Notas |
|---|---|---|
| id | INT PK AI | |
| monto | DECIMAL(12,2) NOT NULL | |
| fecha | DATETIME default CURRENT_TIMESTAMP | |
| descripcion | VARCHAR(255) NOT NULL | |
| categoria | VARCHAR(50) NOT NULL | |
| estudiante_id | INT NOT NULL FK → estudiante.id | ON DELETE CASCADE |

### gasto
Misma estructura que `ingreso`.

### presupuesto
| Columna | Tipo | Notas |
|---|---|---|
| id | INT PK AI | |
| monto_limite | DECIMAL(12,2) NOT NULL | |
| periodo | VARCHAR(50) NOT NULL | p. ej. "Mensual" |
| fecha_inicio | DATE NOT NULL | |
| fecha_fin | DATE NOT NULL | |
| estudiante_id | INT NOT NULL FK → estudiante.id | ON DELETE CASCADE |

### reporte
| Columna | Tipo | Notas |
|---|---|---|
| id | INT PK AI | |
| tipo | VARCHAR(50) NOT NULL | |
| fecha_generacion | DATETIME default CURRENT_TIMESTAMP | |
| total_ingresos | DECIMAL(12,2) default 0 | |
| total_gastos | DECIMAL(12,2) default 0 | |
| estudiante_id | INT NOT NULL FK → estudiante.id | ON DELETE CASCADE |

## 3. Triggers (mantienen saldo_actual)

`saldo_actual = SUM(ingreso) - SUM(gasto)` recalculado tras:

| Trigger | Evento | Tabla |
|---|---|---|
| trg_ingreso_after_insert | AFTER INSERT | ingreso |
| trg_ingreso_after_delete | AFTER DELETE | ingreso |
| trg_gasto_after_insert | AFTER INSERT | gasto |
| trg_gasto_after_delete | AFTER DELETE | gasto |

```sql
UPDATE estudiante SET saldo_actual =
  ((SELECT COALESCE(SUM(monto),0) FROM ingreso WHERE estudiante_id = NEW.estudiante_id)
 - (SELECT COALESCE(SUM(monto),0) FROM gasto   WHERE estudiante_id = NEW.estudiante_id))
WHERE id = NEW.estudiante_id;
```

## 4. Stored procedures

| Procedimiento | Parámetros | Efecto |
|---|---|---|
| `sp_registrar_movimiento` | estudiante_id, tipo, descripcion, monto, categoria, fecha; OUT id, mensaje | Valida tipo/monto e inserta en ingreso o gasto |
| `sp_eliminar_movimiento` | estudiante_id, tipo, movimiento_id; OUT mensaje | Borra solo si pertenece al estudiante |
| `sp_resumen_mensual` | estudiante_id, anio, mes | Devuelve total ingresos, gastos y balance del mes |
| `sp_generar_reporte` | estudiante_id, tipo; OUT reporte_id | Inserta fila en `reporte` con totales |

Ejemplo:
```sql
CALL sp_registrar_movimiento(1, 'Gasto', 'Almuerzo', 12000, 'Alimentación', CURDATE(), @id, @mens);
CALL sp_resumen_mensual(1, YEAR(CURDATE()), MONTH(CURDATE()));
```

## 5. Vista

`vista_resumen_financiero` — join de usuario + estudiante con totales de
ingresos/gastos (subqueries) y la categoría más gastada de cada usuario:

```sql
SELECT * FROM vista_resumen_financiero;
-- usuario_id, nombre, email, estudiante_id, grado, institucion,
-- saldo_actual, total_ingresos, total_gastos, balance, categoria_mas_gastada
```

## 6. Aplicar / regenerar

```powershell
# Desde la raíz del proyecto, con MariaDB encendido (XAMPP):
$sql = Get-Content -Raw -LiteralPath "database\schema.sql"
$sql | C:\xampp\mysql\bin\mysql.exe -u root --default-character-set=utf8mb4
```

El script es idempotente (IF NOT EXISTS / DROP TRIGGER / DROP PROCEDURE).