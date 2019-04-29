import './css/data-table.css';
import React from 'react';
import {useState} from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'

const DataTableAddTags = props => {
    const [tags, setTags] = useState(''); // initial value
    const {handleUpdate, recordItem} = props;

    const _validateInput = (value) => {
        return (/^[a-zA-Z\d\-/: ]*$/.test(value)) ? value : tags;
    };

    const handleChangeTags = e => {
        setTags(_validateInput(e.target.value));
    };

    const handleSubmit = event => {
        event.preventDefault();
        handleUpdate({ tags, recordItem, updateMode: 'add_tags' });  // pass back through function prop
        setTags('');  // clear state
    };

    return (
            <form onSubmit={handleSubmit}>
                <div className={'form-row'}>
                    <div className={'col-10'}>
                        <input type={'text'} value={tags} onChange={handleChangeTags}
                            className={'form-control'} placeholder={'new tag 1 / new tag 2 / new tag 3'} />
                </div>
                    <div className={'col-2'}>
                        <button type={'submit'} value={'submit'} disabled={!recordItem.user_is_admin}
                        className={'btn btn-md btn-warning'}><FontAwesomeIcon icon={'plus'} /></button>
                    </div>
                </div>
            </form>
    )
};

export default DataTableAddTags;