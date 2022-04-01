$('#dtDespesas').DataTable();

$("#politica").hide();

if ($('campo_observacao') == ""){
    $('#observacao').hide();
};

if ($("#forma_pagamento option:selected").val() != 'BOL'){
    $("#documento").hide();
};

function parseDate(str) {
    var date_parts = str.split("/");
    return new Date(date_parts[2], date_parts[1] - 1, date_parts[0]);
};
    
function daysdiff(date1, date2) {
    return Math.floor(1 + ((date2 - date1) / (1000 * 60 * 60 * 24)));
    return (date2 - date1)
};

function toFloat(str) {
    return parseFloat(str.replace(",", "."))
};

function getBusinessDatesCount(startDate, endDate) {
    let count = 0;
    const curDate = new Date(startDate.getTime());
    while (curDate <= endDate) {
        const dayOfWeek = curDate.getDay();
        if(dayOfWeek !== 0 && dayOfWeek !== 6) count++;
        curDate.setDate(curDate.getDate() + 1);
    };
    return count;
};

$("#data_pagamento").on("focusout", function(e){
    var data_pgto = parseDate($("#data_pagamento").val());
    var datediff = daysdiff(Date.now(), data_pgto);
    var hoje = new Date(Date.now());
    var wd_datediff = getBusinessDatesCount(hoje,data_pgto);
    
    if (datediff <= 0) {
        alert("Data inválida.");
    } else if (datediff <= 3 && wd_datediff <= 1) {
        alert("Tempo muito curto para inclusão para pagamento.\nPor favor, altere a data ou inclua o motivo da urgência.");
    }; 
});


$("#tipo").on("change", function(e){

    var forma_pgto = $("#forma_pagamento option:selected").val();
    var tipo = $("#tipo option:selected").val();

    if (tipo !== '50'){
        $("#previsao").show();
    } else {
        $("#previsao").hide();
    };

    if (forma_pgto === 'BOL' && tipo !== '50'){
        $("#documento").show();
    } else {
        $("#documento").hide();
    };

});


$("#forma_pagamento").on("change", function(e){

    var forma_pgto = $("#forma_pagamento option:selected").val();
    var tipo = $("#tipo option:selected").val();

    if (forma_pgto === 'BOL' && tipo !== '50'){
        $("#documento").show();
        $("#observacao").hide();
    } else if (forma_pgto === 'DEP' && tipo !== '50') {
        placeholder = 'Inclua os dados bancários para depósito. '
        $("#campo_observacao").attr('placeholder', placeholder);
        $("#observacao").show();
        $("#documento").hide();
    } else {
        $("#documento").hide();
        $("#observacao").hide();
    };

});


$("#submit_btn").on("click", function(e){

    var data_pgto = parseDate($("#data_pagamento").val());
    var hoje = new Date(Date.now());
    var datediff = daysdiff(hoje, data_pgto);
    var wd_datediff = getBusinessDatesCount(hoje,data_pgto);
    var valor = toFloat($("#valor_pgto").val());
    var obs = $("#campo_observacao").val();
    var previsao = $("#campo_previsao").val();

    if (datediff <= 0) {
        alert("Data inválida.");
        return false;
    } else if (datediff <= 3 && wd_datediff <= 1) {
        alert("Tempo muito curto para inclusão para pagamento.\nPor favor, altere a data ou inclua o motivo da urgência.");
        return false;
    } else if (obs == "") {
        if (valor > 5000 && datediff < 20 && (previsao === null || previsao == "")) {
            alert("Valores acima de R$ 5000,00 devem ter vencimento igual ou maior do que 20 dias.\nDescreva o motivo da urgência no campo 'Observação' ou altere a data.");
            $("#politica").show();
            placeholder = 'Descreva o motivo de urgência deste pagamento.'
            $("#campo_observacao").attr('placeholder', placeholder);
            $('#observacao').show();
            return false;
        } else if (valor > 2500 && datediff < 10 && (previsao === null || previsao == "")) {
            alert("Valores entre R$ 2.500,00 e R$ 5000,00 devem ter vencimento igual ou maior do que 10 dias.\nDescreva o motivo da urgência no campo 'Observação' ou altere a data.");
            $("#politica").show();
            placeholder = 'Descreva a necessidade de urgência deste pagamento.'
            $("#campo_observacao").attr('placeholder', placeholder);
            $('#observacao').show();
            return false;
        } else if (valor > 250 && datediff < 5 && (previsao === null || previsao == "")) {
            alert("Valores entre R$ 250,00 e R$ 2.500,00 devem ter vencimento igual ou maior do que 5 dias.\nDescreva o motivo da urgência no campo 'Observação' ou altere a data.");
            $("#politica").show();
            placeholder = 'Descreva a necessidade de urgência deste pagamento.'
            $("#campo_observacao").attr('placeholder', placeholder);
            $('#observacao').show();
            return false;
        } else if (valor <= 250 && datediff < 2 && (previsao === null || previsao == "")) {
            alert("Valores até R$ 250,00 devem ter vencimento igual ou maior do que 2 dias.\nDescreva o motivo da urgência no campo 'Observação' ou altere a data.\nCUIDADO, pois o prazo para inclusão da despesa no sistema pode chegar a dois dias úteis.");
            $("#politica").show();
            placeholder = 'Descreva a necessidade de urgência deste pagamento.'
            $("#campo_observacao").attr('placeholder', placeholder);
            $('#observacao').show();
            return false;
        };
    };
});


