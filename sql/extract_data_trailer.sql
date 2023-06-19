select distinct
it.board as placa,
cata.nome as cooperado,
cont.e_mail as email,
ende.e_mail as email_2,
uni.fantasia as unidade

from insurance_registration ir 
    left join cliente clio on ir.customer_id = clio.codigo
    left join catalogo cata on cata.cnpj_cpf = clio.cnpj_cpf
    left join insurance_reg_set irs on irs.parent = ir.id
    left join representante r on r.codigo = irs.id_unity
    left join catalogo uni on uni.cnpj_cpf = r.cnpj_cpf
    left join contato cont on cont.cnpj_cpf = clio.cnpj_cpf
    left join endereco ende on ende.cnpj_cpf = clio.cnpj_cpf
    left join insurance_reg_set_coverage irsc on irsc.parent = irs.id
	left join INSURANCE_REG_SET_COV_TRAILER irsct on irsct.PARENT = irsc.ID
    left join insurance_trailer it on it.id = irsct.ID_TRAILER
    left join insurance_status iss on iss.id = irs.id_status
    
where irs.id_status = 7
and it.board <> ''