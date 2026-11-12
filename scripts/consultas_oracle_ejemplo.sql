-- DEMOSTRACION DE PORTAFOLIO. No procede de la empresa ni de una base de datos real.
-- Compatible conceptualmente con Oracle SQL. Tabla y nombres creados para la demo.

-- DDL ilustrativo (ejecutar solo en un esquema de pruebas, previa revision).
CREATE TABLE demo_facturacion (
    id_factura VARCHAR2(30) PRIMARY KEY,
    fecha_emision DATE NOT NULL,
    cliente_id VARCHAR2(30) NOT NULL,
    ejecutivo_id VARCHAR2(30) NOT NULL,
    linea_producto VARCHAR2(40) NOT NULL,
    monto_usd NUMBER(14,2) NOT NULL CHECK (monto_usd >= 0)
);

CREATE INDEX ix_demo_facturacion_fecha_ejecutivo
    ON demo_facturacion (fecha_emision, ejecutivo_id);

-- Ejemplo de agregacion mensual.
SELECT TO_CHAR(fecha_emision, 'YYYY-MM') AS mes,
       ejecutivo_id,
       SUM(monto_usd) AS facturacion_usd,
       COUNT(*) AS cantidad_facturas
FROM demo_facturacion
GROUP BY TO_CHAR(fecha_emision, 'YYYY-MM'), ejecutivo_id
ORDER BY mes, ejecutivo_id;

-- Vista complementaria para reportes (sobre el esquema de pruebas).
CREATE OR REPLACE VIEW demo_facturacion_mensual AS
SELECT TO_CHAR(fecha_emision, 'YYYY-MM') AS mes,
       ejecutivo_id,
       SUM(monto_usd) AS facturacion_usd
FROM demo_facturacion
GROUP BY TO_CHAR(fecha_emision, 'YYYY-MM'), ejecutivo_id;

-- Estos objetos son un ejemplo didactico. No implican que se implementaran
-- indices, vistas ni jobs en el proyecto academico original.
