function AniDice()
{
    myVar=setInterval(rolldice,20)
    document.querySelector('#answer').value = ''
}
var array1 = []
var array2 = []

function rolldice()
{
    let ranNum1 = Math.floor( 1 + Math.random() * 6 );
    let ranNum2 = Math.floor( 1 + Math.random() * 6 );
    let dice1 = document.getElementById("dice1");
    let dice2 = document.getElementById("dice2")
    dice1.src="/static/Dice/dado_" + ranNum1 + ".svg";
    dice2.src="/static/Dice/dado_" + ranNum2 + ".svg";
    array1.push(ranNum1)
    array2.push(ranNum2)

} 

function stopDice()
{
    var answer = array1[array1.length-1] + array2[array2.length - 1]
    document.querySelector('#answer').value = answer
    clearInterval(myVar);
    let coins = Number(document.getElementsByTagName('input')[0].value)
    console.log(coins)
    if ((selection==1) && (answer>7)){
        coins = 2*coins
    }
    $.ajax({ // this is the way to send a post request to the server
        type: "POST", // type of http request method
        contentType: "application/json;charset=utf-8",
        url: "/update", // this is in reference to localhost:5000
        traditional: "true",
        data: JSON.stringify({"name":"rohan"}), // this is necessary
        dataType: "json",
        error : function(e){ // This block is used to define error
            console.log(e)
        }
        });
    
}

var selection = undefined;

var button1 = document.querySelector('#one1')
var button2 = document.querySelector('#two2')
var button3 = document.querySelector('#three3')

function b1(){
    selection = 1
    console.log(selection)
    button1.classList.add('active')
    button2.classList.remove('active')
    button3.classList.remove('active')
    
}

function b2(){
    selection = 2
    console.log(selection)
    button1.classList.remove('active')
    button2.classList.add('active')
    button3.classList.remove('active')
}

function b3(){
    selection = 3
    console.log(selection)
    button1.classList.remove('active')
    button2.classList.remove('active')
    button3.classList.add('active')
}

var input = document.getElementById('Coins')
input.onkeyup = function(){
    console.log('Focused')
    if (isNaN(this.value) == true){
        console.log('value')
        this.style.textDecoration = 'line-through'
    }
    else{
        this.style.textDecoration = 'none'
    }
}

button1.onclick = (b1)
button2.onclick = (b2)
button3.onclick = (b3)

