import {useState} from 'react';


import {useNavigate} from 'react-router-dom';


function Login(){

    const[email,setEmail] = useState('');

    const[password,setPassword] = useState('');

    const[error , setError] = useState('');

    const navigate = useNavigate();


    const handleSubmit = async(e) => {


        e.preventDefault();

        setError('');

        try{

            const response = await fetch('http://localhost:8000/auth/login',{


                method : 'POST',

                headers : {'Content-Type': 'application/json'},
                body: JSON.stringify({email,password}),

            });

            if(!response.ok){

                throw new Error('Invalid credentials');
            }


            const data = await response.json();

            localStorage.setItem('token',data.access_token);

            navigate('/dashboard');
        } catch(err){

            setError(err.message);
        }
    };

   return (

    <div className = "login-container">

        <h2> Login </h2>

        <form onSubmit = {handleSubmit}>

            <input
            type = "email"

            placeholder = "Email"

            value = {email}

            onChange = {e => setEmail(e.target.value)}


            required
         />

         <input 

            type = "password"

            placeholder = "Password"

            value = {password}

            onChange = {e => setPassword(e.target.value)}

            required

          />



          <button type="submit"> Login </button>
 

          {error && <p style = {{color: 'red'}}>{error}</p>}


        </form>
        <p>
            Don't have an account? <a href = "/register">Register</a>
        </p>

        </div>
   );

}


export default Login;