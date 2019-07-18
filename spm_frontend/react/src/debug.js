import { useRef, useEffect } from 'react';

const debugFunctional = (props) => {
    console.log('RENDERED')
    const useTraceUpdate = (props) => {
        const prev = useRef(props);
        useEffect(() => {
            const changedProps = Object.entries(props).reduce((ps, [k, v]) => {
                if (prev.current[k] !== v) {
                    ps[k] = [prev.current[k], v];
                }
                return ps;
            }, {});
            if (Object.keys(changedProps).length > 0) {
                console.log('Changed props:', changedProps);
            }
            prev.current = props;
        });
    }
    useTraceUpdate(props);
}
export default debugFunctional;

////////////// debug Class based component

// componentDidUpdate(prevProps, prevState) {
//     Object.entries(this.props).forEach(([key, val]) =>
//       prevProps[key] !== val && console.log(`Prop '${key}' changed`)
//     );
//     Object.entries(this.state).forEach(([key, val]) =>
//       prevState[key] !== val && console.log(`State '${key}' changed`)
//     );
//   }

// See source: https://stackoverflow.com/questions/41004631/trace-why-a-react-component-is-re-rendering