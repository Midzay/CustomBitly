import React, { Component } from "react";
import ReactDOM from "react-dom";
import axios from 'axios';
import CustomBitly from './components/CustomBitly'



class App extends Component {
    state = {
        long_url: "",
        centerComponent: "",
    }
    // Используем для получения полной ссылки для переадресации
    getUrl() {
        return axios.get('api/get_url/', { params: { short_url: window.location.pathname } })
            .then(res => {
                if (res.data != null) {
                    return res.data['long_url']
                }
            }).catch(err => console.log(err));
    };

    componentDidMount() {
        //  Переходим на полную ссылку 
        if (window.location.pathname != "/") {
            this.getUrl()
                .then((new_url) => {
                    !!new_url && window.location.replace(encodeURI(new_url))
                });
        }
        else {
            this.setState({ centerComponent: <CustomBitly /> });
        }
    }
    render() {
        return (
            <div>

                {this.state.centerComponent}
            </div>
        )
    }
}
export default App;
