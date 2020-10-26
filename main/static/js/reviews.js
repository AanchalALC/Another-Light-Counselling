[...document.querySelectorAll('.mypara')].forEach(function(para) {
    let no_of_words = String(para.innerHTML).split(' ').length
    
    // REDUCE FONT SIZE OF REVIEWS OVER 65 WORDS
    if (no_of_words > 65){
        console.log('Chhotaaed')
        para.classList.add('largereview')
    }
});