import React, { Component } from "react";
import { Button, Row, Col, Card } from "react-bootstrap";
import axios from "axios";
import { throwStatement } from "@babel/types";

export default class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: [],
      selected: false,
      selectedMovies: "",
      rec_data: [],
    };
  }

  componentDidMount = async () => {
    await axios
      .get("http://127.0.0.1:5000/")
      .then((response) => {
        // handle success

        const set = new Set(Object.values(response.data)[0]);
        const array = [...set];
        this.setState(
          {
            data: array,
          },
          () => {}
        );
      })
      .catch((error) => {
        // handle error
        console.log(error);
      })
      .then(() => {
        // always executed
      });
  };

  getRecMov = async () => {
    await axios
      .post("http://127.0.0.1:5000/", {
        mtitle: this.state.selectedMovies.split(" ").slice(0, -1).join(" "),
      })
      .then((response) => {
        // handle success

        console.log(response.data.rec_mov);
        let arr = [];
        for (let i in response.data.rec_mov) {
          arr.push(response.data.rec_mov[i][0]);
        }
        console.log(arr);
        this.setState({
          rec_data: arr,
        });
      })
      .catch((error) => {
        // handle error
        console.log(error);
      })
      .then(() => {
        // always executed
      });
  };

  render() {
    return (
      <div style={{ margin: 20 }}>
        <Row>
          <Col>
            {this.state.selected ? (
              <Button
                variant="primary"
                onClick={() => {
                  this.setState({
                    selected: false,
                  });
                }}
              >
                Home
              </Button>
            ) : (
              <></>
            )}
          </Col>
          <Col>
            <center>
              <h4>Simple Movies Recommendation System</h4>
            </center>
          </Col>
          <Col></Col>
        </Row>
        <br />

        {this.state.selected ? (
          <>
            <center>
              <h5>Selected Movie : {this.state.selectedMovies}</h5>
              <br />
            </center>
            {this.state.rec_data.length > 0 ? (
              <Row>
                <center>
                  <h5> Recommeded Movies</h5>
                </center>
                <br />
                {this.state.rec_data.map((res, index) => {
                  return (
                    <Col xs={12} sm={6} md={3} lg={3}>
                      <Card
                        style={{ marginBottom: 30, cursor: "pointer" }}
                        onClick={() => {
                          console.log("Card", res);
                          this.setState(
                            {
                              selectedMovies: res,
                              selected: true,
                            },
                            () => {
                              this.getRecMov();
                            }
                          );
                        }}
                      >
                        <Card.Body>{res}</Card.Body>
                      </Card>
                    </Col>
                  );
                })}
                <br />
              </Row>
            ) : (
              <center>
                <h4>No Recommended Movies Found</h4>
              </center>
            )}
          </>
        ) : (
          <>
            {this.state.data.length > 0 ? (
              <Row>
                <center>
                  <h5>List of Top Movies</h5>
                </center>
                <br />
                {this.state.data.map((res, index) => {
                  return (
                    <Col xs={12} sm={6} md={3} lg={3}>
                      <Card
                        style={{ marginBottom: 30, cursor: "pointer" }}
                        onClick={() => {
                          console.log("Card", res);
                          this.setState(
                            {
                              selectedMovies: res,
                              selected: true,
                            },
                            async () => {
                              console.log(
                                this.state.selectedMovies
                                  .split(" ")
                                  .slice(0, -1)
                                  .join(" ")
                              );
                              await this.getRecMov();
                            }
                          );
                        }}
                      >
                        <Card.Body>{res}</Card.Body>
                      </Card>
                    </Col>
                  );
                })}
                <br />
              </Row>
            ) : (
              <center>
                <h4>No Movies Found</h4>
              </center>
            )}
          </>
        )}
      </div>
    );
  }
}
