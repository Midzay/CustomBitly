import React, { Component } from 'react';
import axios from 'axios';
import { CopyToClipboard } from 'react-copy-to-clipboard';


export default class CustomBitly extends Component {

    constructor(props) {
        super(props);
        this.state = {
            domain: 'http://localhost:8181/',
            CustomBitlyList: [],
            currentPage: 1,
            perPage: 3,
            shortUrl: {
                long_url: "",
                short_url: "",
            }
        };
        this.handleClick = this.handleClick.bind(this);
    }


    componentDidMount() {
        this.refreshList();
    }
// Получаем  прошлые запросы из базы
    refreshList = () => {
        axios.get('api/shorten/')
            .then(res => {
                console.log(res.data)
                if (res.data != null) {
                    console.log(res.data)
                    const reset = { long_url: "", short_url: "" };
                    this.setState({ CustomBitlyList: res.data, shortUrl: reset });
                }
            }).catch(err => console.log(err));
    };

    handleChange = (e) => {
        let { name, value } = e.target;
        let shortUrl = { ...this.state.shortUrl, [name]: value }
        this.setState({ shortUrl: shortUrl })
    }


    handleSubmit = (event) => {
        event.preventDefault();
        const item = this.state.shortUrl
        axios.post("http://localhost:8181/api/shorten/", item)
            .then((res) => {
                if (res.data['exist']) {
                    alert('Такая ссылка уже существует');
                }
                this.refreshList();

            // }).catch(err => console.log(err));
            }).catch(err => alert("Введите корректный URL"));
    };

    handleClick(event) {
        this.setState({
            currentPage: Number(event.target.id)
        });
    }

    render() {
        // Пагинация данных из базы
        const { CustomBitlyList, currentPage, perPage } = this.state;
        const indexOfLastUrl = currentPage * perPage;
        const indexOfFirstUrl = indexOfLastUrl - perPage;
        const currentUrl = CustomBitlyList.slice(indexOfFirstUrl, indexOfLastUrl);
        const renderTodos = currentUrl.map((item, index) => {
            return (

                <div className="card" key={item.id}>

                    <div className="card-body">
                        <h3 className="card-title"><a href={this.state.domain + item.short_url}>{this.state.domain + item.short_url}</a></h3>
                        <CopyToClipboard text={this.state.domain + item.short_url}>
                            <button type="submit" style={{ float: 'right' }} className="btn btn-primary">Copy</button>
                        </CopyToClipboard>
                        <h6 className="card-text">
                            {(item.long_url.length>50) ?item.long_url.slice(0,50)+'...':item.long_url}
                            </h6>

                    </div>
                </div>
            )
        });

       
        const pageNumbers = [];
        for (let i = 1; i <= Math.ceil(CustomBitlyList.length / perPage); i++) {
            pageNumbers.push(i);
        }

        const renderPageNumbers = pageNumbers.map(number => {
            return (
                <li
                    key={number}
                    id={number}
                    onClick={this.handleClick}
                >
                    {number}
                </li>
            );
        });
        return (
            <div className="main-container ">
                <div className="py-5 text-center">

                    <h2>Создание коротких ссылок</h2>
                    <p className="lead">
                        Для создания короткой ссылки необходимо ввести в поле длинную ссылку, нажать на кнопку "Cократить", скопировать выданную ссылку. В момент перехода по ней пользователь будет переадресован на исходный сайт.</p>
                    <p> Вы можете указать желаемое имя для короткой ссылки для сайта в поле Subpart. Если такая ссылка не занята вы сможете ее использовать. </p>
                </div>

                <div className="row">

                    <div className="col-md-12 order-md-1">

                        <form className="needs-validation" noValidate onSubmit={this.handleSubmit}>
                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <label htmlFor="firstName">Вставьте сюда ссылку</label>
                                    <input type="text" className="form-control" name="long_url"
                                        id="long_url" value={this.state.shortUrl.long_url} required onChange={this.handleChange} placeholder="Url" />
                                </div>
                                <div className="col-md-6 mb-3">
                                    <label htmlFor="lastName">Subpart</label>
                                    <input type="text" className="form-control" id="subpart" name="short_url"
                                        value={this.state.shortUrl.short_url} required onChange={this.handleChange} placeholder="subpart" />

                                </div>
                            </div>


                            <hr className="mb-4" />
                            <button className="btn btn-primary btn-lg btn-block" onClick={this.handlesubmitForm} >Сократить</button>
                        </form>
                    </div>
                </div>

                <footer className="my-5 pt-5 text-muted text-center text-small">
                    <h4 className="d-flex justify-content-between align-items-center mb-3">
                        <span className="text-muted">Ваши ссылки</span>
                        <span className="badge badge-secondary badge-pill">{this.state.CustomBitlyList.length}</span>
                    </h4>
                    <div>
                        {renderTodos}
                    </div>

                    <div>
                        <ul>

                        </ul>
                        <ul id="page-numbers">
                            {renderPageNumbers}
                        </ul>
                    </div>
                </footer>
            </div>

        )
    }

}



