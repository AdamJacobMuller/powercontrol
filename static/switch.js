function changePort(port) {
    $.ajax({
        url     : '/port/'+port.id+'/state/'+port.value,
        accept  : 'application/json',
        success : function(data) {
                port.value=data
            },
        error: function(data) {
            alert('got an error')
            }
    });
}

function changeset(set) {
    $.ajax({
        url     : '/set/'+set.id+'/state/'+set.value,
        accept  : 'application/json',
        success : function(data) {
                set.value=data
            },
        error: function(data) {
            alert('got an error')
            }
    });
}
