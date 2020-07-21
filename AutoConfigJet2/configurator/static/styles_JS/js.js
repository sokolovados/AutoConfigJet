$('#submit').on('click', function () {
  let region = document.querySelector('title')
  console.log(region.text)
  let form = $('#form')
  $.ajax({
    type: "POST",
    url: '/autoconfig/'+region.text,
    data: form.serialize(),
    success: function (response) {
      const errors = response['errors']
      if (response['result']) {
        for (error in errors) {
          let input = document.getElementById(error)
          input.classList.remove('is-valid')
          input.classList.remove('is-invalid')
          input.classList.add('is-valid')
          if (input.nextElementSibling) {
            input.nextElementSibling.classList.replace('invalid-feedback', 'valid-feedback')
            input.nextElementSibling.innerHTML = 'Вы великолепны'
          }
        }

        let download = document.querySelector('#download')
        download.href = '/config_download'+response['path']
        $("#myModal").modal('show')
        $("#modalBody").html(response['result'].join('<br>').replace(/startreplace/gi, '<b style="color: Green">').replace(/endreplace/gi, '</b>'))
      }

      else {
        for (error in errors) {
          let input = document.getElementById(error)
          console.log(input.nextElementSibling)
          if (input.nextElementSibling) {
            if (errors[error][0]) {
              input.classList.remove('is-valid')
              input.classList.remove('is-invalid')
              input.classList.add('is-invalid')
              input.nextElementSibling.classList.replace('valid-feedback', 'invalid-feedback')
              input.nextElementSibling.innerHTML = errors[error][0]
            } else {
              input.classList.remove('is-valid')
              input.classList.remove('is-invalid')
              input.classList.add('is-valid')
              input.nextElementSibling.classList.replace('invalid-feedback', 'valid-feedback')
              input.nextElementSibling.innerHTML = 'Вы великолепны'
            }
          }
        }
      }
    }
  })
})


$('#sendTftp').on('click', function () {
  let url = '{{url}}'
  $.ajax({
    type:    'POST',
    url:     '/tftpload',
    data:    url,
    success: function (data) {
    }
  })
})


let modelRequest = function () {
  $('#model').find('option').remove()
  $.ajax({
    type:     'POST',
    dataType: 'json',
    url:      '/sqlmodel',
    data:     JSON.stringify({vendor: ($('#vendor')).val(),
              region: (($('title')).text())
              }),
    success:  function (models) {
      for (model in models) {
        $('#model').append(new Option(models[model], models[model]))
      }
    }
  })
}
$('#vendor').change(modelRequest)
            .ready(modelRequest)

$('#multicastCheckBox').change(function () {
  if (this.checked) {
    $('#multicast_vlan').prop('disabled', false)

  } else {
    $('#multicast_vlan').removeClass('is-invalid')
                        .removeClass('is-valid')
    $('#multicast_vlan').prop('disabled', true)
      .val('')
      .next().removeClass('is-valid')
      .next().removeClass('is-invalid')
  } 
})

$('#multicast_vlan').ready(function () {
  $('#multicastCheckBox').prop("checked", false)
  $('#multicast_vlan').prop('disabled', true)
                      .val('')

})

