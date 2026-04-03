/** code by webdevtrick ( https://webdevtrick.com ) **/
const listItems = document.querySelectorAll('.main li');
const allimages = document.querySelectorAll('.main .container-fluid .images');
const container = document.querySelector('#gallery');

function toggleActiveClass(active){
    listItems.forEach(item => {
      item.classList.remove('active');
    })
    active.classList.add('active');
}

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}
 
function toggleimages(dataClass){
    const imagesArray = Array.from(allimages);
    
    if(dataClass === 'all'){
        // Randomize order for 'All' view
        shuffle(imagesArray);
        imagesArray.forEach(img => {
            img.style.display = 'block';
            container.appendChild(img);
        });
    } else {
        // Sort by position attribute for specific categories
        imagesArray.sort((a, b) => parseInt(a.dataset.position) - parseInt(b.dataset.position));
        imagesArray.forEach(img => {
            if (img.dataset.class === dataClass) {
                img.style.display = 'block';
            } else {
                img.style.display = 'none';
            }
            container.appendChild(img);
        });
    }
}

// Initialize: Shuffle if 'All' is active by default
document.addEventListener('DOMContentLoaded', () => {
    const activeItem = document.querySelector('.main li.active');
    if (activeItem && activeItem.dataset.class === 'all') {
        toggleimages('all');
    }
});
 
listItems.forEach(item => {
    item.addEventListener('click', function(){
        toggleActiveClass(item);
        toggleimages(item.dataset.class);
    });
});