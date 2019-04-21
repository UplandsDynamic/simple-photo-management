import './css/data-table.css';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import Paginate from './paginate.js';
import React from 'react';

class DataTableNav extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            term: '',
        };

    }

    componentWillMount() {
        this.setState({
            term: this.props.record.meta.search,
        });
    }

    componentWillReceiveProps(nextProps) {
        this.setState({
            term: nextProps.record.meta.search,
        });
    }

    getRecords() {
        let record = this.props.record;
        Object.assign(record.meta, {page: 1});
        this.props.handleGetRecords({record});
    }

    handleProcessPhotos({scan=false, retag=false, clean_db=false} = {}){
        this.props.handleProcessPhotos({scan, retag, clean_db});
    }

    handleSearch(e) {
        let record = this.props.record;
        this.props.handleSearch({record, term: e.target.value});
        this.setState({term: e.target.value});
    }

    render() {
        const {userIsAdmin} = this.props.authMeta;
        if (this.props.record) {
            let {record} = this.props;
            return (
                <React.Fragment>
                    <div className={'container'}>
                        <div className={'row nav-row'}>
                            <div className={'col-12'}>
                                <div className={'btn-group float-right'}>
                                    <nav className="nav-pagination float-right" aria-label="Table data pages">
                                        <Paginate record={record}
                                                  handleGetRecords={this.props.handleGetRecords}
                                        />
                                    </nav>
                                </div>
                            </div>
                        </div>
                        <div className={'row nav-row'}>
                            <div className={`${userIsAdmin ? 'col-4' : 'col-2'}`}>
                                <div className={'btn-group'}>
                                    <button onClick={this.getRecords} className={'btn btn-md btn-success mr-1 '}>
                                        <FontAwesomeIcon icon={"sync-alt"}/></button>
                                    <button onClick={userIsAdmin ? () => this.handleProcessPhotos({ scan: true }) : null} 
                                        className={`btn btn-md btn-warning mr-1 ${!userIsAdmin ? 'disabled' : ''}`}>
                                        <FontAwesomeIcon icon={"plus"}/></button>
                                    <button onClick={userIsAdmin ? () => this.handleProcessPhotos({retag: true}) :null} 
                                    className={`btn btn-md btn-warning mr-1 ${!userIsAdmin ? 'disabled' : ''}`}>
                                        <FontAwesomeIcon icon={"tags"}/></button>
                                        <button onClick={userIsAdmin ? () => this.handleProcessPhotos({clean_db: true}) :null} 
                                        className={`btn btn-md btn-warning mr-1 ${!userIsAdmin ? 'disabled' : ''}`}>
                                        <FontAwesomeIcon icon={"broom"} /></button>
                                </div>
                            </div>
                            <div className={`${userIsAdmin ? 'col-8' : 'col-10'}`}>
                                <nav className={'search-navigation w-100 d-block ml-1'}>
                                    <input value={this.state.term} placeholder={'Search'}
                                           name={'search'} className={'form-control search'}
                                           onChange={(e) => {this.handleSearch(e)}
                                           }/>
                                </nav>
                            </div>
                        </div>
                    </div>
                </React.Fragment>
            )
        }
        return null;
    }
}
export default DataTableNav;