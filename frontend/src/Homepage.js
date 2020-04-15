import React, {useState, useEffect, useLayoutEffect, useRef} from "react";
import ReactDOM from "react-dom";
import {makeId, debounce} from "./utils";


const routes = {
    jobs: 'jobs'
};

let global_loadMoreJobs = {
    'is_loading': false,
    'has_more': true,
    'total': 0
};

const JobListing = (props) => (
    <div className="job-panel">
        <div className="counter">
            {props.count}
        </div>
        <div className="content">
            <div className="header">
                <p className="title">{props.data.title}</p>
            </div>
            <div className="body">
                <p>{props.data.description.slice(0, 150) + '...'}</p>
            </div>
            <div className="footer">
                <p>{props.data.skills.map((skill, i) => skill ? (i > 0 ? ', ' + skill : skill) : '')}</p>
            </div>
        </div>
    </div>
);

const Search = ({setSearchTerm, setJobs, setJobsPage}) => {
    const [query, setQuery] = useState('');
    return (
        <form className="search-form" action="" onSubmit={e => {
            global_loadMoreJobs.total = 0;
            e.preventDefault();
            setJobs([]);
            setJobsPage(0);
            setSearchTerm(query);
        }}>
            <input type="text"
                   placeholder="search..."
                   value={query}
                   onChange={e => setQuery(e.target.value)}
            />
            <button type="submit">search</button>
        </form>
    )
};




let firstRun = true;


function App() {

    const [jobs, setJobs] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [jobsPage, setJobsPage] = useState(0);
    // const [firstRun, setFirstRun] = useState(true);
    const [loadMoreJobs, setLoadMoreJobs] = useState(global_loadMoreJobs);

    const getJobs = () => {
        let url = routes.jobs + "?page=" + jobsPage + (searchTerm ? "&term=" + searchTerm : '');
        setLoadMoreJobs({
            ...global_loadMoreJobs,
            bottom_message: 'Waiting for results ...'
        });
        const fetchJobs = async () => {
            fetch(url).then(response => {
                if (response.status !== 200) {
                    console.log('Error!')
                }
                return response.json();
            }).then(data => {
                global_loadMoreJobs = {
                    'is_loading': false,
                    'has_more': data.stats.count === data.stats.page_size,
                    'total': global_loadMoreJobs.total + data.stats.count
                };
                setJobs(jobs.concat(data.items));
                setLoadMoreJobs({
                    ...global_loadMoreJobs,
                    top_message: 'Displaying ' + global_loadMoreJobs.total + ' results out of ' + data.stats.total,
                    bottom_message: global_loadMoreJobs.has_more ? 'Scroll down to load more' : 'No more results :('
                })
            })
        };
        setTimeout(fetchJobs, 2000);
    };

    useEffect(() => {
        getJobs();
    }, [searchTerm]);

    const handleScroll = debounce(() => {
        // check if we are at bottom of page
        if (window.innerHeight + document.body.scrollTop - document.documentElement.offsetHeight >= -20) {
            // initiate request for load more
            if (global_loadMoreJobs.has_more && !global_loadMoreJobs.is_loading) {
                console.log('loading more jobs...');
                global_loadMoreJobs = {
                    ...global_loadMoreJobs,
                    'is_loading': true,
                };
                setJobsPage(prevPage => prevPage + 1);
            }
        }
    }, 250);


    useEffect(() => {
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll)
    }, []);

    useLayoutEffect(() => {
        if (!firstRun) {
            console.log('new page', jobsPage);
            getJobs();
        } else {
            firstRun = false;
        }
    }, [jobsPage]);

    return (
        <div className="container">
            <Search setSearchTerm={setSearchTerm} setJobs={setJobs} setJobsPage={setJobsPage}/>
            <div className="job-listings">
                <p>{loadMoreJobs.top_message}</p>
                {
                    jobs.map((job, i) => (<JobListing key={makeId(4)} data={job} count={i + 1}/>))
                }
                <p>{loadMoreJobs.bottom_message}</p>
            </div>
        </div>
    )
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App/>, wrapper) : null;