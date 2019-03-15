$('#dtDespesas').DataTable();

$("#politica").hide();
if ($('campo_observacao') == ""){
    $('#observacao').hide();
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

$(".btn").on("click", function(e){

    var data_pgto = parseDate($("#data_pagamento").val());
    var datediff = daysdiff(Date.now(), data_pgto);
    var valor = toFloat($("#valor_pgto").val());
    var obs = $("#campo_observacao").val();
    var previsao = $("#campo_previsao").val();

    if (datediff <= 0) {
        alert("Data inválida.");
        return false;
    } else if (obs == "") {
        if (datediff == 1) {
            alert("Vencimento menor do que 2 dias.\nJustifique a urgência em 'Observação', ou altere a data.");
            $("#politica").show();
            placeholder = 'Justifique a necessidade de urgência deste pagamento.'
            $("#campo_observacao").attr('placeholder', placeholder);
            $('#observacao').show();
            return false;
        } else if (datediff < 5 && valor < 500 && (previsao === null || previsao == "")) {
            alert("Valores até R$ 500,00 devem ter vencimento igual ou maior do que 5 dias.\nJustifique a urgência em 'Observação' ou altere a data.");
            $("#politica").show();
            placeholder = 'Justifique a necessidade de urgência deste pagamento.'
            $("#campo_observacao").attr('placeholder', placeholder);
            $('#observacao').show();
            return false;
        } else if (datediff < 15 && valor >= 500  && valor < 5000 && (previsao === null || previsao == "")) {
            alert("Valores entre R$ 500,00 e R$ 5000,00 devem ter vencimento igual ou maior do que 15 dias.\nJustifique a urgência em 'Observação' ou altere a data.");
            $("#politica").show();
            placeholder = 'Justifique a necessidade de urgência deste pagamento.'
            $("#campo_observacao").attr('placeholder', placeholder);
            $('#observacao').show();
            return false;
        } else if (datediff < 30 && valor >= 5000 && (previsao === null || previsao == "")) {
            alert("Valores acima de R$ 5000,00 devem ter vencimento igual ou maior do que 30 dias.\nJustifique a urgência em 'Observação' ou altere a data.");
            $("#politica").show();
            placeholder = 'Justifique a necessidade de urgência deste pagamento.'
            $("#campo_observacao").attr('placeholder', placeholder);
            $('#observacao').show();
            return false;
        };
    };
});


