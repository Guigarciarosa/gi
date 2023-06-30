SELECT DISTINCT lm.placa, lm.marca, lm.modelo, lm.ano_fabricacao, lm.ano_modelo, lm.tipo_veiculo, 
lm.valor_fipe,  lm.valor_da_contratacao, lm.unidade, lm.status, lm.conjunto, lm.matricula, lm.beneficio, lm.inicio_vigencia
FROM "listagem_mestra" as lm 
WHERE lm.beneficio IN ('RASTREADOR','RASTREADOR REBOQUE/SEMIRREBOQUE') 
AND lm.placa NOT LIKE 'SEM-PLACA'