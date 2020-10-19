var answer_offset = -44;

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}




function toggleFaq(thediv){

    // GET THE STUFF
    let qdiv = document.getElementById(thediv.id);
    let answer = document.getElementById(qdiv.dataset.answer);
    let indicator = qdiv.lastElementChild
    let curr_state = indicator.innerHTML;   

        
    if (curr_state == "-"){
        // GET INITIAL HEIGHT
        let height = (answer.clientHeight - answer_offset).toString() + "px";
        answer.classList.add("hidden");
        answer.style.marginBottom = "-" + height;
        answer.style.paddingBlock = "0px";
        indicator.innerHTML = "+";

        setTimeout(() => {
            answer.style.display = "none";
        }, 200);

    } else {
        // SHOW IF HIDDEN
        answer.style.display = "block";

        setTimeout(() => {
            answer.classList.remove("hidden");
            answer.style.marginBottom = "unset";
            answer.style.paddingBlock = "1rem";
            
        }, 100);
        
        indicator.innerHTML = "-";
    }

}

document.addEventListener("DOMContentLoaded", function(event) { 
    
    // HIDE ALL
    let questions = document.getElementsByClassName('question');
    for (let question of questions){
        toggleFaq(question);
    }

    // SET SENSIBLE OFFSET
    answer_offset = 32;

});