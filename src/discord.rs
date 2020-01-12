use serde::Deserialize;
use serde_json;

use std::collections::HashSet;

use parking_lot::RwLock;

use serenity::{
    model::gateway::Ready,
    prelude::*,
};

use super::error;
use super::files;
use super::picture;

const SLEEP_INTERVAL: u64 = 60 * 60 * 3;

struct Handler {
    api: files::Api,
    previous: RwLock<HashSet<String>>,
}
impl Handler {
    fn new(api: files::Api, previous: HashSet<String>) -> Self {
        Handler {
            api,
            previous: RwLock::new(previous),
        }
    }
}

impl EventHandler for Handler {
    fn ready(&self, ctx: Context, ready: Ready) {
        dbg! {"ready"};

        // get all the channels to broadcast cat pictures too
        let channels = ready
            .guilds
            .into_iter()
            .map(|x| x.id().channels(&ctx))
            .filter(|x| x.is_ok())
            .map(|x| x.unwrap())
            .map(|x| x.into_iter().filter(|(_x, y)| y.name.contains("cat")))
            .flatten()
            .map(|(_x, y)| y)
            .collect::<Vec<_>>();

        // loop forever to keep sending pictures out
        loop {
            // dbg! {"cycling outer"};

            loop {
                // dbg! {"cycling inner"};

                let file_path = 
                {
                    let mut prev = self.previous.write();

                    // find a picture from the cache that we can post
                    picture::find_picture(&mut prev, &self.api)

                };

                // dbg! {"file path found,", &file_path};

                if let Ok(path) = file_path {

                    let mut break_out = true;

                    let p = std::path::Path::new(&path);

                    // cycle through channels and post the picture
                    channels.iter().for_each(|channel| {
                        // send pictures until there is one without an error
                        let response = channel.send_files(&ctx, vec![p], |x| x);
                        // file was sent, quit
                        if let Ok(_) = response {
                            dbg! {"posted, good"};
                        }
                        // there was an error sensding the file to discord so we repeat the cycle
                        else {
                            dbg! {"error. redoing"};
                            std::thread::sleep(std::time::Duration::from_secs(2));
                            break_out = false;
                        }
                    });

                    if break_out {
                        break
                    }

                } else {
                    continue;
                }
            }

            let dur = std::time::Duration::from_secs(SLEEP_INTERVAL);
            std::thread::sleep(dur);
        }
    }
}

#[derive(Debug, Deserialize)]
struct DiscordConfig {
    id: u64,
    secret: String,
    token: String,
}

impl DiscordConfig {
    fn new() -> Result<Self, error::DiscordError> {
        let file = std::fs::File::open("config.json")?;
        let r: Self = serde_json::from_reader(file)?;

        Ok(r)
    }
}

pub fn start_bot(previous: HashSet<String>, api: files::Api) -> Result<(), error::DiscordError> {
    let config = DiscordConfig::new()?;

    let handler = Handler::new(api, previous);

    let mut bot = Client::new(config.token, handler)?;

    if let Err(why) = bot.start() {
        println! {"bot error!!!"}
        dbg! {&why};
        return Err(error::DiscordError::from(why));
    }

    Ok(())
}
