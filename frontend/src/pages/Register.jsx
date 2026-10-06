import {useState} from 'react';


import {useNavigate} from 'react-router-dom';

function Register(){

    const [name,setName] =useState('');

    const[email,setEmail] = useState('');

    const[password,setPassword] = useState('');

    const[error , setError] = useState('');

    const navigate = useNavigate();


    const handleSubmit = async (e) => {
      e.preventDefault();
      setError('');
      try {
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Registration failed');
      }
      navigate('/');
      } catch (err) {
      setError(err.message);
      }
};


return (

    <div className = "register-container">

        <h2> Register </h2>

        <form onSubmit = {handleSubmit}>

         <input 

           type = "text"

           placeholder = "Name"

           value = {name}

           onChange = {e => setName(e.target.value)}
           required
         />

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



          <button type="submit"> Register </button>
 

          {error && <p style = {{color: 'red'}}>{error}</p>}


        </form>
        <p>
            Already have an account? <a href = "/">Login</a>
        </p>

        </div>
   );

}




export default Register;
