const API_URL="http://127.0.0.1:8000";

function runSearch(){
    console.log("runSearch triggered");
    const query=document.getElementById("searchInput").value;
    if(query.trim()===""){
        alert("Please type something to search for.");
        return;
    }

    const infoText=document.getElementById("infoText");
    const resultsGrid=document.getElementById("resultsGrid");
    infoText.innerText="Searching...";
    resultsGrid.innerHTML="";
    fetch(API_URL+"/search?query="+encodeURIComponent(query))
        .then(function(response){
            if (!response.ok){
                throw new Error("Server responded with status "+response.status);
            }
            return response.json();
        })
        .then(function (data){
            const results=data.results.results;
            const count=data.results.count;
            const timeMs=data.results.search_time_ms;
            infoText.innerText="Found "+count+" result(s) in "+timeMs+"ms";

            if(count===0){
                resultsGrid.innerHTML="";
                const noResults=document.createElement("div");
                noResults.className="no-results";
                noResults.innerText="No matching images found. Try a different search.";
                resultsGrid.appendChild(noResults);
                return;
            }

            for(let i=0;i<results.length;i++){
                const item=results[i];
                const card=document.createElement("div");
                card.className="card";
                card.style.animationDelay=(i*0.05)+"s";
                const img=document.createElement("img");
                img.src=item.url;
                img.alt=item.image;
                card.onclick=function(){
                    openModal(item.url);
                };
                card.appendChild(img);
                resultsGrid.appendChild(card);
            }
        })
        .catch(function(error){
            infoText.innerText="Something went wrong: "+error.message;
            console.error("Search error:",error);
        });
}

function uploadImages(inputId){
    console.log("uploadImages triggered for",inputId);
    const fileInput=document.getElementById(inputId);
    const uploadStatus=document.getElementById("uploadStatus");

    if(fileInput.files.length===0){
        return;
    }

    const formData=new FormData();
    for(let i=0;i<fileInput.files.length;i++){
        formData.append("files",fileInput.files[i]);
    }

    uploadStatus.style.color="#9a99a8";
    uploadStatus.innerText="Uploading "+fileInput.files.length+" image(s)... this may take a moment.";

    fetch(API_URL+"/upload",{
        method:"POST",
        body:formData
    })
        .then(function(response) {
            if (!response.ok){
                throw new Error("Server responded with status "+response.status);
            }
            return response.json();
        })
        .then(function(data){
            const uploadedCount=data.uploaded.length;
            const skippedCount=data.skipped.length;
            uploadStatus.style.color="#4ade80";
            uploadStatus.innerText=
                "✓ Added "+uploadedCount+" new image(s), skipped "+skippedCount+" ("+data.total_images+" total). You can search now.";
            fileInput.value="";
        })
        .catch(function(error){
            uploadStatus.style.color="#f87171";
            uploadStatus.innerText="Upload failed: "+error.message;
            console.error("Upload error:",error);
        });
}

function openModal(imageUrl){
    const modal=document.getElementById("modalOverlay");
    const modalImage=document.getElementById("modalImage");
    modalImage.src=imageUrl;
    modal.classList.add("active");
}

function closeModal(){
    const modal=document.getElementById("modalOverlay");
    modal.classList.remove("active");
}

document.getElementById("searchInput").addEventListener("keyup",function(event){
    if (event.key==="Enter"){
        runSearch();
    }
});