import streamlit as st
import random
import pandas as pd
import networkx as nx
import plotly.graph_objs as go



def get_rand_vote(party_member_list, party_candidate_list):

    signer = random.sample(party_member_list, 1)
    recipient = random.sample(party_candidate_list, 1)
    return signer, recipient

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

    #for node, adjacencies in enumerate(G.adjacency()):
    #    node_info = adjacencies[0] +' # of connections: '+str(len(adjacencies[1]))
    #    node_trace['text']+=tuple([node_info])
    
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


with st.sidebar:
    st.subheader("Set Seed for Random Number Generator")
    st.write("When using the same seed, the generated dataset will be the same.")
    random_seed = st.number_input("RNG Seed", value=10)
    random.seed(random_seed)

st.header("State Party Election Prototype")

st.subheader("Generate Elections Data")

col1, col2 = st.columns(2)
with col1:
    num_party_members = st.number_input("Number of Unique Party Members", min_value=2, max_value=1000, value=300)
    num_party_candidates = st.number_input("Number of Candidates", min_value=1, max_value=1000, value=10)
with col2:
    num_votes = st.number_input("Total Signatures", min_value=1, max_value=10000, value=300)


party_member_list = list(range(1,num_party_members+1))
party_member_list_name = ["voter" + str(val).zfill(4) for val in party_member_list]

party_candidate_list = list(range(1, num_party_candidates+1))
party_candidate_list_name = ["candidate" + str(val).zfill(4) for val in party_candidate_list]


vote_list = []
for vote_num in range(num_votes):
    
    signer, recipient = get_rand_vote(party_member_list, party_candidate_list)

    vote_info = [vote_num, signer, recipient]
    vote_list.append(vote_info)
    
votes_df = pd.DataFrame(vote_list, columns=["Time", "Signer", "Recipient"])
st.write("Voting Record")
st.dataframe(votes_df)

st.subheader("Tabulate Elections Results")

col3, col4 = st.columns(2)

with col3:
    num_sig_member = st.number_input("Number of Signatures per Party Member", value=1)
with col4:
    num_sig_req = st.number_input("Number of Signatures for Candidacy", value=15)


G = nx.DiGraph()

# Get nodes
node_vals = votes_df["Signer"].tolist()
node_vals = [val[0] for val in node_vals]
candidates = votes_df["Recipient"].tolist()
candidates = [val[0] for val in candidates]
node_vals.extend(candidates)

node_vals = list(set(node_vals))

G.add_nodes_from(node_vals)

num_good_votes = 0
num_bad_votes = 0

for index, row in votes_df.iterrows():
    edge_tail = row["Signer"][0]
    edge_head = row["Recipient"][0]

    # Check for multiple votes cast
    # Maybe weight double votes as 0 and legitimate votes as 1
    tail_out_degree = G.out_degree(edge_tail)
    if (tail_out_degree < num_sig_member):
        G.add_edge(edge_tail, edge_head)
        num_good_votes += 1
    else:
        num_bad_votes += 1

with col3:
    st.metric("Legitimate Votes", num_good_votes)
with col4:
    st.metric("Illegitimate Votes", num_bad_votes)

successful_candidates = [party_candidate_list_name[node-1] for (node, val) in G.degree() if (val > num_sig_req)]

st.write("Candidates with Sufficient Votes")
successful_candidates

st.subheader("Voter Network Visualization")
visualize_plotly(G)



