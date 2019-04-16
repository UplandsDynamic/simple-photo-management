import './css/data-table.css';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import React from 'react'

const DataTableData = ({record = {}, formatUTCDateTime, authMeta = {}} = {}) => {
    const {authenticated, userIsAdmin} = authMeta;
    if (!record || !authenticated || (record && record.data.results.length < 1)) {
        return (
            <tr data-toggle="modal" className={'d-flex dataTableRows'}>
                <td className={'col-12 no-data'}>
                    <div className={'alert alert-warning'}> Loading data ...</div>
                </td>
            </tr>
        )
    }
    return record.data.results.map((item, index) => {
        let {
            datetime_of_request, file_format, file_name, id, owner, tags, user_is_admin, public_img_url,
            public_img_tn_url
        } = item;
        let rowClasses = ['d-flex', 'dataTableRows'];
        let imgClasses = ['img-fluid', 'img-thumbnail', 'd-block', 'mx-auto'];
        let img_url = `${process.env.REACT_APP_ROUTE}${public_img_tn_url}/${file_name}-150_150${file_format}`;
        return (<tr key={item.id} data-toggle="modal" className={rowClasses.join(' ')}>
            {/*<th scope="row">{item.id}</th>*/}
            <td className={'col-5 photo'}><img src={img_url} alt={tags[0]} className={imgClasses.join(' ')}/>
            </td>
            <td className={'col-5 tags'}>
                <ul>
                    {tags.map((tag, key) => <li key={key}>{tag}</li>)}
                </ul>

            </td>
            <td className={'action-col col-2 text-center'}>-</td>
        </tr>)
    });
};

export default DataTableData;

/*
Note 1: Be sure to pass values (e.g. {...item}) rather than obj (e.g. {item}),
otherwise the item obj (corresponding to the data results on the main table) will be updated with
values input in the console, as data.updateData would essentially
point to data.results, rather than being a separate, discrete object.
 */