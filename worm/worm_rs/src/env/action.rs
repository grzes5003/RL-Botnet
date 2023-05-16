

#[derive(Copy, Clone, Eq, PartialEq, Hash)]
pub enum Actions {
    NONE,
    PING,
    SCAN,
    INFECT,
    FETCH_INFO
}

impl Actions {
    fn sample() -> Actions {
        Actions::NONE
    }

    pub fn get_reward(&self) -> i32 {
        match self {
            Actions::NONE => 0,
            Actions::PING => 1,
            Actions::SCAN => 2,
            Actions::INFECT => 3,
            Actions::FETCH_INFO => 4
        }
    }

    pub fn from(action: usize) -> Self {
        match action {
            0 => Actions::NONE,
            1 => Actions::PING,
            2 => Actions::SCAN,
            3 => Actions::INFECT,
            4 => Actions::FETCH_INFO,
            _ => Actions::NONE
        }
    }

    pub fn iter() -> impl Iterator<Item = Self> {
        [Actions::NONE, Actions::PING, Actions::SCAN, Actions::INFECT, Actions::FETCH_INFO]
            .iter()
            .copied()
    }
}


struct ActionBot {
    is_busy: bool,
}

impl ActionBot {
    fn new() -> ActionBot {
        ActionBot
    }

    pub fn action(&self, action: Actions) -> Result<(), usize> {
        if self.is_busy {
            return Err(-1);
        }

        match action {
            Actions::NONE => self.none(),
            Actions::PING => self.ping(),
            Actions::SCAN => self.scan(),
            Actions::INFECT => self.infect(),
            Actions::FETCH_INFO => self.fetch_info()
        };

        Ok(())
    }

    fn none(&self) {
        println!("none");
    }

    fn ping(&self) {
        println!("ping");
    }

    fn scan(&self) {
        println!("scan");
    }

    fn infect(&self) {
        println!("infect");
    }

    fn fetch_info(&self) {
        println!("fetch_info");
    }
}