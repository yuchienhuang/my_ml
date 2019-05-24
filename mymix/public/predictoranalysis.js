$(function() {  
    $('form').submit(function(event) {
      event.preventDefault();
      
      let song = $('input[name="song"').val();
      let artist = $('input[name="artist"]').val();
      
      $.getJSON('/feature_table?' + $.param({song: song, artist: artist}), function(data) {
        $('input[type="text"]').val('');
        $('input').focus();
        
        
        //let obj = jQuery.parseJSON( data );

        let table = data.trackdf
        let link = data.link;
        let artists = data.artists
       
        const albumDiv = document.getElementById('albumlink');
        albumDiv.appendChild(StoryDOMObject(link,artists,newtab=true));

      

        const tableDiv = document.getElementById('print');
        tableDiv.innerHTML = table;

        
         
         
        
        });
        return false;
      });
    });
  

    function StoryDOMObject(web_link,artist,newtab=false) {
      const card = document.createElement('div');
      // card.setAttribute('id', storyJSON._id);
      card.className = 'story card';
    
      const cardBody = document.createElement('div');
      cardBody.className = 'card-body';
      card.appendChild(cardBody);
    
      const creatorSpan = document.createElement('a');
      creatorSpan.className = 'story-creator card-title';
      creatorSpan.innerHTML = artist;
      creatorSpan.setAttribute('href', web_link);
      if(newtab == true){
        creatorSpan.target = "_blank"
      }
      cardBody.appendChild(creatorSpan);
    
      // const contentSpan = document.createElement('p');
      // contentSpan.className = 'story-content card-text';
      // console.log(storyJSON );
      // contentSpan.innerHTML = storyJSON.energy;
      // cardBody.appendChild(contentSpan);
    
      const cardFooter = document.createElement('div');
      cardFooter.className = 'card-footer';
      card.appendChild(cardFooter);
    
    
      return card;
    }