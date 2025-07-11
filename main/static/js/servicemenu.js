function toggleDropdown() {
    // ONLY RUN IF WIDTH IS LESS THAN MOBILE SIZE
    if (window.innerWidth < 790) {
        let dropdowndiv = document.getElementById('dropdowncontent')
        dropdowndiv.classList.toggle('visible')
    }
}

function toggleDropdownDoIFeel() {
    // ONLY RUN IF WIDTH IS LESS THAN MOBILE SIZE
    if (window.innerWidth < 790) {
        let dropdowndiv = document.getElementById('dropdowncontentdoifeel')
        dropdowndiv.classList.toggle('visible')
    }
}

function toggleDropdownplan() {
    // ONLY RUN IF WIDTH IS LESS THAN MOBILE SIZE
    if (window.innerWidth < 790) {
        let dropdowndiv = document.getElementById('dropdowncontentplan')
        dropdowndiv.classList.toggle('visible')
    }
}
// function toggleDropdownHowToFeel() {
//     // ONLY RUN IF WIDTH IS LESS THAN MOBILE SIZE
//     if (window.innerWidth < 790) {
//         let dropdowndiv = document.getElementById('dropdowncontenthowtofeel')
//         dropdowndiv.classList.toggle('visible')
//     }
// }

document.addEventListener('DOMContentLoaded', function (event) {

    let servicebutton = document.getElementById('servicebutton')
    servicebutton.addEventListener('click', toggleDropdown)

    let doifeelbutton = document.getElementById('doifeelbutton')
    doifeelbutton.addEventListener('click', toggleDropdownDoIFeel)

    let planbutton = document.getElementById('planbutton')
    planbutton.addEventListener('click', toggleDropdownplan)
    // let howtofeelbutton = document.getElementById('howtofeelbutton')
    // howtofeelbutton.addEventListener('click', toggleDropdownHowToFeel)

})