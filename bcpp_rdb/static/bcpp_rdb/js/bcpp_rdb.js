function bcppRdbHomeReady( context ) {
    /* Prepare page elements */
    var djContext = JSON.parse( context );
    // var csrftoken = Cookies.get( 'csrftoken' );

    // // configure AJAX header with csrftoken
    // $.ajaxSetup({
    // beforeSend: function(xhr, settings) {
    //     if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
    //         xhr.setRequestHeader("X-CSRFToken", csrftoken);
    //         };
    //     };
    // });
    $('[data-toggle="tooltip"]').tooltip();
    $.each( djContext.file_items, function( key ) {
      $( '#id-link-refresh-' + djContext.file_items[key].name ).click( function (e) {
        e.preventDefault();
        updateCSV( djContext.file_items[key], djContext.upload_url );    
      });
    });
    $.each( djContext.test_file_items, function( key ) {
      $( '#id-link-refresh-' + djContext.test_file_items[key].name ).click( function (e) {
        e.preventDefault();
        updateCSV( djContext.test_file_items[key], djContext.upload_url );    
      });
    });
}

function updateCSV( file_item, upload_url ) {
    $( '#id-link-refresh-' + file_item.name ).addClass( 'fa-spin' );
    $( '#id-link-refresh-' + file_item.name ).attr( 'title', 'fetching new CSV for ' + file_item.name );
    $( '#id-fetch-data-' + file_item.name ).removeClass( 'alert-success' );
    $( '#id-fetch-data-' + file_item.name ).addClass( 'alert-info' );
    $( '#id-alert-text-' + file_item.name ).text( 'Fetching new ' + file_item.verbose_name + ' from the remote research database. This will take a few minutes.' );
    $( '#id-fetch-data-' + file_item.name ).show();

    var url = Urls['update-csv-file']( file_item.name );
    var ajaxCsv = $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        processData: false,
    });

    ajaxDownload = ajaxCsv.then( function ( data ) {
      var fnames = [];
      $.each( data, function( key ) {
        $( '#id-link-refresh-' + file_item.name ).removeClass( 'fa-spin' );
        $( '#id-link-refresh-' + file_item.name ).attr( 'title', 'click to fetch CSV for ' + file_item.name );
        $( '#id-current-file-last-updated-' + file_item.name ).text( file_item.current_file.timestamp );
        $( '#id-fetch-data-' + file_item.name ).removeClass( 'alert-info' ).addClass( 'alert-success' );
        $( '#id-alert-text-' + file_item.name ).text( 'Done.' );
        fnames.push(data[key].filename);
      });
      return fnames;
    });

    ajaxDownload.done( function ( fnames ) {
        $.each( fnames, function( index, fname ) {
          window.open( upload_url + fname, '_blank' );
        });
    });

    ajaxCsv.fail( function( jqXHR, textStatus, errorThrown ) {
      console.log( textStatus + ': ' + errorThrown );
      $( '#id-link-refresh-' + file_item.name ).removeClass( 'fa-spin' );
      $( '#id-link-refresh-' + file_item.name ).attr( 'title', 'click to fetch CSV for ' + file_item.verbose_name );
      $( '#id-fetch-data-' + data[key].file_item.name ).removeClass( 'alert-info' ).removeClass( 'alert-success' ).addClass( 'alert-danger' );
      $( '#id-alert-text-' + file_item.name ).text( 'Error.' );
    });
    return true;
}