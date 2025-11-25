const droparea = document.getElementById('droparea');
const fileInput = document.getElementById('fileInput');
const filelist = document.getElementById('filelist');

//open file dialog on click
droparea.addEventListener('click',()=>{
    fileInput.click();
})

//when files selected by click
fileInput.addEventListener("change", (e)=>{
    handleFiles(e.target.files);
});

//Prevent default drag behaviors of browser
['dragenter','dragover','dragleave','drop'].forEach(event => {
    droparea.addEventListener(event,(e)=>e.preventDefault());
});

//Highlight on darg over the drop area
fileInput.addEventListener('dragover',()=>{
    droparea.style.background="#e8f0ff";
});

//Remove highlight when drag leaves drop area
fileInput.addEventListener('dragleave',()=>{
    droparea.style.background="#f5f9ff";
});

//Handle dropped files
droparea.addEventListener("drop",(e)=>{
    const files = e.dataTransfer.files;
    handleFiles(files);
    droparea.style.background="#e8f0ff";
});

//Function to handle files
function handleFiles(files){
    for (let file of files){
        if (!file.name.endsWith('.md') && !file.name.endsWith('.markdown')) {
            alert("Only markdown files are allowed!");
            continue;       
        }
        const reader = new FileReader();
        reader.onload=(e)=>{
            console.log("markdown content:",e.target.result);
            //Here you can process the markdown content as needed

           //Create list item for each file
            const li = document.createElement('li')
            li.textContent=file.name;
            filelist.appendChild(li);

            //yahan hum apne graphs ke logic call kr skte hain
            //generateGraph(e.target.result);

        };

        reader.readAsText(file);   
         
    }
}