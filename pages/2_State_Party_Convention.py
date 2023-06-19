import streamlit as st
import math
import pandas as pd
import networkx as nx
import plotly.graph_objs as go


def visualize_plotly(G):
    #Use plotly to visualize the network graph created using NetworkX
    #Adding edges to plotly scatter plot and specify mode='lines'
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=1,color='#888'),
        hoverinfo='none',
        mode='lines')

    pos = nx.kamada_kawai_layout(G) 
    for n, p in pos.items():
        G.nodes[n]['pos'] = p

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    #Adding nodes to plotly scatter plot
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            size=20,
            line=dict(width=0)))

    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
    
    #Plot the final figure
    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title="Voter Network", #title takes input from the user
                    title_x=0.45,
                    titlefont=dict(size=25),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    st.plotly_chart(fig, use_container_width=True) #Show the graph in streamlit



def clean_sig_csv(raw_sig_df):

    #st.dataframe(raw_sig_df)

    #df_sliced = raw_sig_df.loc[:,"Candidate for Governor":"Signee Election Code.6"]
    #st.dataframe(df_sliced)

    response_list = []
    for idx, row in raw_sig_df.iterrows():
        row_list = row.tolist()
        row_list = [item for item in row_list if isinstance(item, str) or not math.isnan(item)]
        response_list.append(row_list)
    
    response_df = pd.DataFrame(response_list, columns=["time", "email", "position", "candidate", "file", "election_id", "signature", "city"])
    response_df["election_id"] = response_df["election_id"].str.upper()

    return response_df

def get_good_candidates(G, num_sig_req):
    return [node for node, val in G.degree() if (val >= num_sig_req)]

def main():
    

    st.header("State Party Election Prototype")

    st.subheader("Upload Signatures Data")

    csv_file_upload = st.file_uploader("Upload Signatures Responses", type="csv")

    if (csv_file_upload is not None):

        sig_df_raw = pd.read_csv(csv_file_upload)
        sig_df_clean = clean_sig_csv(sig_df_raw)

    else:
        st.info("No file uploaded.")
        st.stop()


    st.subheader("Tabulate Signatures Data")

    # Get unique voters
    unique_voters = sig_df_clean["election_id"]
    unique_voters = list(set(unique_voters))


    unique_races = sig_df_clean["position"].tolist()
    unique_races = list(set(unique_races))
    #print(unique_races)

    race_params = {x : (1, 30) if ("Court" not in x) else (7,30) for x in unique_races }
    #print(race_params)

    graph_dict = {x : nx.DiGraph() for x in unique_races}
    for key, graph in graph_dict.items():
        graph.add_nodes_from(unique_voters)



    votes_dict = {x : {'good':0,'bad':0} for x in unique_races}

    # Main for loop iteration through
    for idx, row in sig_df_clean.iterrows():
        race_holder = row["position"]
        edge_head = row["candidate"]
        edge_tail = row["election_id"]

        tail_out_degree = graph_dict[race_holder].out_degree(edge_tail)
        if (tail_out_degree < race_params[race_holder][0]):
            graph_dict[race_holder].add_edge(edge_tail, edge_head)
            votes_dict[race_holder]["good"] += 1
        else:
            votes_dict[race_holder]["bad"] += 1


    successful_candidates = {race : get_good_candidates(graph_dict[race], race_params[race][1]) for race in unique_races}

    successful_candidates


    extra_details_race = st.selectbox("Race Details", unique_races)
    print(extra_details_race)


    if extra_details_race is not None:
        vote_status_dict = votes_dict[extra_details_race]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Votes", vote_status_dict["good"]+vote_status_dict["bad"])
        with col2:
            st.metric("Legitimate Votes", vote_status_dict["good"])
        with col3:
            st.metric("Illegitimate Votes", vote_status_dict["bad"])

        visualize_plotly(graph_dict[extra_details_race])

main()

