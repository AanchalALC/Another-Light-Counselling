function toggleDropdown(){
    // ONLY RUN IF WIDTH IS LESS THAN MOBILE SIZE

    if (window.innerWidth < 790){
        let dropdowndiv = document.getElementById('dropdowncontent')
        dropdowndiv.classList.toggle('visible')
    }
}

document.addEventListener('DOMContentLoaded', function(event){
    
    let servicebutton = document.getElementById('servicebutton')
    servicebutton.addEventListener('click', toggleDropdown)

})