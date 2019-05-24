$(function() {  
  $('form').submit(function(event) {
    event.preventDefault();
    
    let song = $('input[name="song"').val();
    let artist = $('input[name="artist"]').val();
    
    $.get('/search?' + $.param({song: song, artist: artist}), function(string) {
      $('input[type="text"]').val('');
      $('input').focus();
      
      if(sessionStorage.length ==0){sessionStorage.setItem("have searched?", "Yes")}
      

      if(string==""){

        location.reload();

        

       }else {
        if(string.substring(0, 3)=='not'){
          const spotifyDiv = document.getElementById('results');
          spotifyDiv.innerHTML = "";  
          const azlyricsDiv = document.getElementById('no results');
          azlyricsDiv.innerHTML = string;
          

        }else{
          const spotifyDiv = document.getElementById('results');
          spotifyDiv.innerHTML = "";
          const azlyricsDiv = document.getElementById('no results');
          azlyricsDiv.innerHTML = string;

        }
        

        
      }
       
       
      
      })
    });
  });
