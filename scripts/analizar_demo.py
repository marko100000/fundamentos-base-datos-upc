"""Demostración independiente: KPIs sobre datos 100 % sintéticos, sin conexiones reales."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'datos_sinteticos'
OUT = ROOT / 'resultados_demo'


def leer_y_validar(nombre: str, columnas: set[str], clave: list[str]) -> pd.DataFrame:
    df = pd.read_csv(DATA / nombre)
    faltantes = columnas - set(df.columns)
    if faltantes:
        raise ValueError(f'{nombre}: faltan columnas {sorted(faltantes)}')
    if df[list(columnas)].isna().any().any():
        raise ValueError(f'{nombre}: se encontraron nulos')
    if df.duplicated(subset=clave).any():
        raise ValueError(f'{nombre}: claves duplicadas en {clave}')
    return df


def main() -> None:
    facturas = leer_y_validar('facturacion.csv',
        {'id_factura','fecha_emision','ejecutivo_id','cliente_id','monto_usd','linea_producto'},
        ['id_factura'])
    cuotas = leer_y_validar('cuotas.csv',
        {'ejecutivo_id','mes','cuota_usd'}, ['ejecutivo_id','mes'])
    oportunidades = leer_y_validar('oportunidades.csv',
        {'id_oportunidad','ejecutivo_id','mes','cliente_id','estado','valor_estimado_usd','probabilidad_cierre'},
        ['id_oportunidad'])

    if (facturas['monto_usd'] < 0).any() or (cuotas['cuota_usd'] <= 0).any():
        raise ValueError('Montos o cuotas fuera de rango')
    if not oportunidades['probabilidad_cierre'].between(0,1).all():
        raise ValueError('Probabilidades fuera de rango')

    facturas['mes'] = pd.to_datetime(facturas['fecha_emision']).dt.strftime('%Y-%m')
    fact_agg = facturas.groupby(['ejecutivo_id','mes'],as_index=False).agg(
        facturacion_usd=('monto_usd','sum'), cantidad_facturas=('id_factura','count'))
    kpi = cuotas.merge(fact_agg, on=['ejecutivo_id','mes'], how='left', validate='one_to_one')
    kpi[['facturacion_usd','cantidad_facturas']] = kpi[['facturacion_usd','cantidad_facturas']].fillna(0)
    kpi['cumplimiento_pct'] = (kpi['facturacion_usd'] / kpi['cuota_usd'] * 100).round(2)

    pipeline = oportunidades.groupby(['mes','estado'],as_index=False).agg(
        oportunidades=('id_oportunidad','count'),
        valor_pipeline_usd=('valor_estimado_usd','sum'))
    mensual = kpi.groupby('mes',as_index=False).agg(
        facturacion_usd=('facturacion_usd','sum'), cuota_usd=('cuota_usd','sum'))
    mensual['cumplimiento_pct'] = (mensual['facturacion_usd']/mensual['cuota_usd']*100).round(2)

    # Control independiente entre agregados.
    assert round(float(facturas['monto_usd'].sum()),2) == round(float(kpi['facturacion_usd'].sum()),2)
    OUT.mkdir(exist_ok=True)
    kpi.to_csv(OUT / 'kpi_por_ejecutivo.csv',index=False)
    mensual.to_csv(OUT / 'kpi_mensual.csv',index=False)
    pipeline.to_csv(OUT / 'pipeline_mensual.csv',index=False)
    print('OK: validaciones completadas. Datos 100 % ficticios.')
    print('Registros facturas:',len(facturas),'cuotas:',len(cuotas),'oportunidades:',len(oportunidades))
    print('Facturacion total demo (USD):', round(float(facturas['monto_usd'].sum()),2))
    print('Resultados generados en',OUT)

if __name__ == '__main__':
    main()
