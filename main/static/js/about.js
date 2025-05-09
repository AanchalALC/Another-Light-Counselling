const expandDiv = (divObj) => {
    let paras = divObj.children

    // REMOVE HIDDEN FROM ALL PARAGRAPHS
    for(let i=0; i<paras.length; i++){
        paras[i].classList.remove('hidden')
    }

    // SET DIV STATE
    divObj.dataset.state = "expanded"

}

const collapseDiv = (divObj) => {
    let paras = divObj.children

    // ADD HIDDEN TO ALL PARAGRAPHS
    for(let i=0; i<paras.length; i++){
        paras[i].classList.add('hidden')
    }

    // AND REMOVE HIDDEN FROM FIRST
    paras[0].classList.remove('hidden')

    // SET DIV STATE
    divObj.dataset.state = "collapsed"
    
}


// WHEN EXPAND BUTTON CLICKED
const toggleInfo = (button) => {
    let infoDiv = document.getElementById(button.dataset.id)
    
    if (infoDiv.dataset.state === "collapsed"){
        expandDiv(infoDiv)
        button.innerHTML = "LESS"
    } else {
        collapseDiv(infoDiv)
        button.innerHTML = "READ MORE"
    }
}



// INITIALLY HIDE EXTRA PARAS
let infodivs = document.getElementsByClassName('memberinfo')
for(var i = 0; i < infodivs.length; i++){
    collapseDiv(infodivs[i])
}