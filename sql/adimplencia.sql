select distinct
        irs.id as conjunto,
        case 
            when cast(bx.data_baixa as varchar) <> '' then 'Adimplente'
            else 'Inadimplente' 
        end as status_financeiro
        from titulo_movimento tm
        left join invoice_item ii on tm.id_titulo_movimento = ii.id_title_moviment
        left join invoice i on i.id = ii.parent
        left join insurance_reg_set irs on i.id_set = irs.id
        left outer join representante r on r.codigo = irs.id_unity
        left outer join catalogo cata on cata.cnpj_cpf = r.cnpj_cpf
        left outer join (
            select 
            max(tb.data_lancamento) data_baixa,
            sum(tb.valor_baixa) as valor_baixa,
            tb.ponteiro
            from titulo_movimento tb 
            inner join situacao_documento stb on tb.codigo_situacao_documento = stb.codigo
            where 
            tb.historico not in(1,5)
            and tb.crc_cpg = 'R'
            and stb.entra_fluxo_caixa = 'S'
            and (tb.ponteiro_consolidado is null or tb.ponteiro_consolidado = 0)
            group by 
            tb.ponteiro
        ) bx on tm.ponteiro = bx.ponteiro
        where irs.id_status = 7