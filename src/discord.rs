use serde::Deserialize;
use serde_json;

use std::collections::HashSet;
use tokio::sync::RwLock;

use serenity::async_trait;
use serenity::{model::gateway::Ready, prelude::*};

use super::error;
use super::files;
use super::picture;

// post a single picture a day
const SLEEP_INTERVAL: u64 = 60 * 60 * 24;

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

#[async_trait]
impl EventHandler for Handler {
    async fn ready(&self, ctx: Context, ready: Ready) {
        // get all the channels to broadcast cat pictures too
        let mut _channels = Vec::new();

        for guild in ready.guilds.into_iter() {
            let channels = guild.id().channels(&ctx).await;
            if let Ok(channels) = channels {
                for (_channel_id, guild_channel) in channels.into_iter() {
                    if guild_channel.name.contains("cat") {
                        _channels.push(guild_channel)
                    }
                }
            }
        }

        let channels = _channels;

        // loop forever to keep sending pictures out
        loop {
            loop {
                let file_path = {
                    let mut prev = self.previous.write().await;

                    // find a picture from the cache that we can post
                    picture::find_picture(&mut prev, &self.api).await
                };

                // dbg! {"file path found,", &file_path};

                if let Ok(path) = file_path {
                    let mut break_out = true;

                    let p = std::path::Path::new(&path);

                    // cycle through channels and post the picture
                    for channel in channels.iter() {
                        let response = channel.send_files(&ctx, vec![p], |x| x).await;

                        // file was sent, quit
                        if let Ok(_) = response {
                        }
                        // there was an error sending the file to discord so we repeat the cycle
                        else {
                            std::thread::sleep(std::time::Duration::from_secs(2));
                            break_out = false;
                        };
                    }

                    if break_out {
                        break;
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

pub async fn start_bot(
    previous: HashSet<String>,
    api: files::Api,
) -> Result<(), error::DiscordError> {
    let config = DiscordConfig::new()?;

    let handler = Handler::new(api, previous);

    let mut bot = Client::builder(&config.token)
        .event_handler(handler)
        .await?;

    if let Err(why) = bot.start().await {
        println! {"bot error!!!"}
        dbg! {&why};
        return Err(error::DiscordError::from(why));
    }

    Ok(())
}
