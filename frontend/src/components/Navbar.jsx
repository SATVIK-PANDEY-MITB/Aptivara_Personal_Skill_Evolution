import {Link,useNavigate} from 'react-router-dom';


function Navbar() {

    const navigate = useNavigate();


    const handleLogout = () => {

        localStorage.removeItem('token');

        navigate('/');
    };


    return (

        <nav className = "navbar">

            <Link to = "/dashboard"> Dashboard</Link>

            <button onClick = {handleLogout}> Logout</button>
        </nav>
    );
}


export default Navbar;