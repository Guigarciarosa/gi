SELECT DISTINCT lm.placa, lm.conjunto, lm.matricula, lm.valor_fipe, lm.beneficio, lm.inicio_vigencia
FROM "listagem_mestra" as lm 
WHERE lm.beneficio IN ('RASTREADOR','RASTREADOR REBOQUE/SEMIRREBOQUE') AND lm.placa NOT LIKE 'SEM-PLACA'
AND lm.status = 'ATIVO'